#!/usr/bin/env python
# -*- coding:utf-8 -*-

# --------------------------------
# Author: shenjh@snail.com
# Date: 2015-05-22
# Usage:
# --------------------------------

from django.core.management.base import BaseCommand
import traceback
import logging
import time
import datetime
import json
from optparse import make_option
from ujobs.utils.redisclient import rc
from ujobs.releaseinfo import *
from ujobs.utils.utils import send_single_api_request
import signal
from settings import TIME_FMT

'''
    get agent info periodic
'''

logger = logging.getLogger('logger_agent')

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--pid-file', dest='pid_file'),
    )

    help = ""

    def handle(self, **options):
        pid_file = options.get('pid_file', "")
        if pid_file:
            with open(pid_file, 'a') as f:
                f.write("%d\n" % os.getpid())
        while 1:
            try:
                self.run()
            except:
                error = traceback.format_exc()
                print error
                logger.error('#### error in agentinfo: %s' % (error))
            time.sleep(5 * 60)


    def run(self):
        print 'start:', datetime.datetime.now().strftime(TIME_FMT)
        logger.debug('#### start updating agent info...')

        self.update_cache()
        self.update_info()
        self.check_conflict_minions()

        logger.debug('##### end agent info update!')
        print 'end:', datetime.datetime.now().strftime(TIME_FMT)

    def update_cache(self):
        '''
            update cached agent list.

            1. get syndic manage.status.
            2. get master manage.status.

        '''
        print 'cache start:', datetime.datetime.now().strftime(TIME_FMT)
        ###### test syndic alive ######
        status_ok,ping_result = send_single_api_request('syndic*','test.ping')
        logger.debug("ping syndic result:{0}".format(ping_result))
        print ping_result
        if not ping_result:
            logger.warning("### ping result empty, start self-kill !!")
            os.kill(os.getpid(),signal.SIGTERM)
            return

        syndic_ups = set()
        syndic_downs = set()

        for key,value in ping_result.iteritems():
            if value == True:
                syndic_ups.add(key)
            else:
                syndic_downs.add(key)

        # current_total_downs = set(syndic_downs)
        current_total_ups = set(syndic_ups)

        if len(current_total_ups)==0:
            logger.warning("@@@@@ total up minion num is 0, restart process")
            os.kill(os.getpid(),signal.SIGTERM)
            return
        # note: here we assume test.ping will show down syndic in result.
        syndics = syndic_downs.union(syndic_ups)
        rc.set(STATUS_RESULT_MASTER_KEY,json.dumps({"down":list(syndic_downs),"up":list(syndic_ups)}))

        ###### start test minion alive ######
        if len(syndic_ups)>0:
            logger.debug("## start syndic exec: salt-run manage.status --out json")
            status_ok,minion_result = send_single_api_request(list(syndic_ups),"cmd.run",["salt-run manage.status --out json"],expr_form="list")
            if not status_ok:
                logger.warning("!!! manage.status return fail, abort this update.")
                return
            for syndic,resp in minion_result.iteritems():
                logger.debug('### start handle syndic:%s'%syndic)
                if resp:
                    # clean output.
                    resp = resp[resp.index("{"):]
                    resp = resp.replace('\n','')
                    try:
                        syndic_resp = json.loads(resp)
                    except:
                        logger.warning("## syndic return format error!")
                        logger.warning("msg:%s"%(resp))
                        print "Format invalid:",resp
                        continue
                    syn_ups = syndic_resp.get('up')
                    syn_downs = syndic_resp.get('down')

                    # get sync report downs and ups.
                    # current_total_downs = current_total_downs.union(set(syn_downs))
                    if syn_ups:
                        current_total_ups = current_total_ups.union(set(syn_ups))
                    else:
                        logging.debug("None up agent under syndic:{0}".format(syndic))

                    # store status result for each sub-master
                    syndic_resp.update({"timestamp":datetime.datetime.now().strftime(TIME_FMT)})
                    rc.set(SYNDIC_RESULT_PREFIX+syndic,json.dumps(syndic_resp))

                    # If syndic is alive, remove previous result before refresh.
                    # If syndic is down, just keep last minionss in redis and later set them to down status.
                    rc.delete(SYNDIC_MINIONS_PREFIX+syndic)
                    if syn_downs:
                        rc.sadd(SYNDIC_MINIONS_PREFIX+syndic,*syn_downs)
                        # set the direct master of minion in redis.
                        [rc.hset(DETAIL_KEY_PREFIX+agent,'master',syndic) for agent in syn_downs]
                    if syn_ups:
                        rc.sadd(SYNDIC_MINIONS_PREFIX+syndic,*syn_ups)
                        [rc.hset(DETAIL_KEY_PREFIX+agent,'master',syndic) for agent in syn_ups]
                else:
                    logger.warning('syndic manage.status is empty, skip redis update.')
                logger.debug('### end handle syndic:%s'%(syndic))

        ### set master id of syndic and get actual total clients ###
        # master_id = salt.utils.network.generate_minion_id()
        status_ok,masters_result = send_single_api_request(list(syndics),'grains.item',arg=['master'],expr_form='list')
        if not status_ok:
            return

        total_clients = set(syndics)
        for syndic in syndics:
            logger.debug('start get minions from %s'%syndic)
            key = SYNDIC_MINIONS_PREFIX+syndic
            rc.hset(DETAIL_KEY_PREFIX+syndic,'master',masters_result.get(syndic,{}).get("master",''))# set master result of syndic.
            if rc.exists(key):
                # get current minions in redis, this includes current ups and last downs of syndics.
                total_clients = total_clients.union(rc.smembers(key))
            else:
                logger.debug('syndic has no minions, skip:%s'%(key))

        ##### calc actual total downs #######
        current_total_downs = total_clients.difference(current_total_ups)

        if current_total_downs:
            logger.debug("start verify down agent status...")
            status_ok,ping_result = send_single_api_request(list(current_total_downs),'test.ping',expr_form='list')
            if status_ok and isinstance(ping_result,dict):
                for key,value in ping_result.iteritems():
                    if value == True:
                        logger.debug("change status down to up, agent: {0},value:{1}".format(key,value))
                        current_total_downs.remove(key)
                        current_total_ups.add(key)
            else:
                logger.warning("verify result==> status: {0}, ping result:{0}".format(status_ok,ping_result))

        ##### refresh redis current status #####
        rc.refresh_set(MINIONS_SET_KEY,total_clients)
        rc.refresh_set(MINIONS_DOWN_SET_KEY,current_total_downs)
        rc.refresh_set(MINIONS_UP_SET_KEY,current_total_ups)

        cache = {
            'up':list(current_total_ups),
            'down':list(current_total_downs)
        }
        rc.set(STATUS_RESULT_KEY, json.dumps(cache))
        rc.set(RESULT_TIMESTAMP_KEY, datetime.datetime.now().strftime(TIME_FMT))

        ### set ip:minion_id map for client minions
        for mid in total_clients:
            key = IP_KEY_PREFIX + mid
            if mid and mid[0] in ['1','2'] and not rc.exists(key):
                logger.debug("set ip minion-id redis mapping: "+key)
                rc.set(key, mid)
        print 'cache end:', datetime.datetime.now().strftime(TIME_FMT)

    def update_info(self):
        '''
            update info of all minions.
        '''
        def _update_info(_agents):
            logger.debug("start request grains.items, len: {0}, count:{1}".format(len(_agents),count))
            status_ok,results = send_single_api_request(_agents, 'grains.items',arg=[], expr_form='list', timeout=60)

            if not isinstance(results,dict):
                logger.error("agent info is not a dict:{0}".format(results))
                return
            missing_minions = set(_agents).difference(set(results.keys()))
            logger.debug("len of result:{0}, missing_minions:{1}".format(len(results),",".join(missing_minions)))
            logger.debug("start update cache for each agent...")
            for agent,infos in results.iteritems():
                detail_key = DETAIL_KEY_PREFIX + agent
                if not infos:
                    logger.warning("###info is None, skip update,agent:{0}".format(agent))
                    print "###info is None, skip update,agent:{0}".format(agent)
                    continue

                if not isinstance(infos,dict):
                    logger.warning("info is not a dict, please check state,agent:{0}".format(agent))
                    print "info is not a dict,agent:{0},{1}".format(agent,infos)
                    continue
                # save all grains info.
                if 'master' in infos.keys():
                    infos['master_ip'] = infos['master']
                    del infos['master']
                rc.hmset(detail_key,infos)

                os = infos.get("os", "")
                osrelease = infos.get("osrelease", "")
                ipv4 = infos.get("ipv4", [])
                kernel = infos.get("kernel", "")
                saltversion = infos.get("saltversion", "")
                locale_info = infos.get("locale_info", {})

                #### update os release ####
                if os and osrelease:
                    rc.hset(detail_key, 'os_version', os+" "+osrelease)

                #### update network ip_addr ####
                if ipv4 and isinstance(ipv4,list):
                    if "127.0.0.1" in ipv4:
                        ipv4.remove("127.0.0.1")

                    tmp_list = list(ipv4)
                    for item in tmp_list:
                        if item.startswith("169.254"):
                            rc.delete(IP_KEY_PREFIX + item)
                            ipv4.remove(item)

                    rc.hset(detail_key, 'ip', ", ".join(ipv4))
                    for ip in ipv4:
                        rc.set(IP_KEY_PREFIX + ip, agent)  # set ip, agent map, may have more ips.

                #### update saltversion ####
                if saltversion:
                    rc.hset(detail_key, 'salt_version', 'Salt: '+saltversion)

                #### update os type ####
                if kernel:
                    rc.hset(detail_key, 'kernel', kernel)

                #### update local info ####
                if locale_info:
                    rc.hset(detail_key,'locale_info',locale_info)
                    rc.hset(detail_key,"default_encoding",locale_info.get("defaultencoding",""))

                rc.hset(detail_key, 'ctime', datetime.datetime.now().strftime(TIME_FMT))  # set receive time
                rc.hset(detail_key,'last_timestamp',int(time.time()))
            return missing_minions

        logger.debug('start update all minion info ...')
        agents = rc.smembers(MINIONS_UP_SET_KEY)
        if len(agents)==0:
            logger.warning(" up agents is 0, return.")
            return
        new_agents = set()
        current = time.time()
        for client in agents:
            detail_key = DETAIL_KEY_PREFIX + client
            last_timestamp = rc.hget(detail_key,'last_timestamp') if rc.hexists(detail_key,'last_timestamp') else 0
            # if not last_timestamp or current-eval(last_timestamp)>60*60*24:
            if not rc.exists(detail_key):
                # logger.debug("===> schedule agent_info update :"+client+",last is:"+str(last_timestamp))
                new_agents.add(client)
                continue
            ips = rc.hget(detail_key,'ip')
            if ips:
                for ip in ips.split(","):
                    rc.set(IP_KEY_PREFIX + ip, client)  # set ip, agent map, may have more ips.

            rc.hset(detail_key, 'ctime', datetime.datetime.now().strftime(TIME_FMT))  # set receive time
        agents = list(new_agents)
        if len(agents)==0:
            logger.debug("no new agent need to update, return!")
            return
        block = 300
        agent_list = [agents[i:i+block] for i in range(0,len(agents),block)]
        logger.debug("==> total num: {0}, total round: {1}".format(len(agents),len(agent_list)))
        count = 0
        missing_minions = set()
        for _agents in agent_list:
            count +=1
            missing_minions = missing_minions.union(_update_info(_agents))
        missing_count = len(missing_minions)
        trial = 0
        if missing_count>0:
            logger.debug("start update missing minions, count:{0}, minions:{1}".format(missing_count,",".join(missing_minions)))
            while trial<3:
                missing_minions = _update_info(list(missing_minions))
                missing_count = len(missing_minions)
                if missing_count==0:
                    logger.debug("### OK, all minions info refreshed!")
                    break
                logger.debug("trial:{2}, still missing minions left: {0}, minions:{1}".format(missing_count+1,",".join(missing_minions),trial))
                trial+=1

        logger.debug("final missing update minions: {0}".format(",".join(missing_minions)))
        logger.debug('end update all minion info!')

        ## 删除可能不存在的IP
        # clients = rc.smembers(MINIONS_SET_KEY)
        clients = set()
        [clients.add(item.split(':')[-1]) for item in rc.keys(DETAIL_KEY_PREFIX+"*")]
        current_ips = rc.smembers(MINIONS_SET_KEY)
        for client in clients:
            ips = rc.hget(DETAIL_KEY_PREFIX + client,'ip')
            if ips:
                [current_ips.add(ip.strip()) for ip in ips.split(',')]

        last_ips = set()
        [last_ips.add(ip.split(':')[-1]) for ip in rc.keys(IP_KEY_PREFIX+"*")]
        diff = last_ips - current_ips
        logger.warning('diff ip list size: {0}, detail:{1}'.format(len(diff),','.join(diff)))
        for ip in diff:
            # logger.warning('delete old redis key:{0}'.format(IP_KEY_PREFIX+ip))
            rc.delete(IP_KEY_PREFIX+ip)

    def check_conflict_minions(self):
        ## 检查minion是否在多个syndic下, 如果有则重新设置其master值.
        clients = rc.smembers(MINIONS_UP_SET_KEY)
        conf_clients = set()
        for client in clients:
            detail_key = DETAIL_KEY_PREFIX + client
            if str(client).startswith("syndic"):
                logger.debug("ignore syndic:{0}".format(client))
                continue
            master = rc.hget(detail_key,'master')
            master_ip = rc.hget(detail_key,'master_ip')
            if not master_ip:
                logger.warning("!!!!! agent has no master_ip, agent:{0}".format(detail_key))
                continue
            actual_master = rc.get(IP_KEY_PREFIX+master_ip)
            if master and actual_master and actual_master != master:
                if client == "" or client == None or client == "None":
                    logger.warning("!!!! None client detected, check syndic:{0}".format(actual_master))
                    continue
                conf_clients.add(client)
                logger.warning("conflict master, syndic:{0},minion:{1}, actual:{2}".format(master,client,actual_master))
                rc.hset(detail_key,'master',actual_master)
                _,rm_result = send_single_api_request(master,'cmd.run',arg=['echo y|salt-key -d {0}'.format(client)])
                logger.debug(rm_result)
                ### delete then do a grain update.
                rc.delete(detail_key)
        logger.debug("conflict clients check done, total updated:{0}, minions:{1}".format(len(conf_clients),",".join(conf_clients)))
        if len(conf_clients) > 0:
            logger.debug("start re-update conflict minions' info...")
            self.update_info()

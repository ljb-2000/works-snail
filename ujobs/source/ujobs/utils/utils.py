#!/usr/bin/env python
# -*- coding:utf-8 -*-

# --------------------------------
# Author: shenjh@snail.com
# Date: 2015/6/3
# Usage:
# --------------------------------

import datetime
import os, errno
import logging
import traceback
from settings import MEDIA_ROOT
import re
import requests, json
import time
from releaseinfo import REL_FILE_UPLAOD_FOLDER, FILESRCIP,UJOBS_API_HOST, \
    SALT_MASTER_PASSWD,SALT_MASTER_USER,FILE_SERVER_HOST,MAPPED_FILE_SERVER_HOST,\
    IP_KEY_PREFIX, MINIONS_UP_SET_KEY,DETAIL_KEY_PREFIX
from apps.files.models import FileInfo,UploadRecord
from enums import enum_script, enum_template, enum_job, enum_history
import ssl
from functools import wraps
import hashlib
from redisclient import rc
from service import _history, _job, _user
from apps.history.models import HistoryFileInfo, RunningResult, ScheduleHistory
from apps.jobs.models import JobFileInfo, JobStepPushFile,JobStepPullFile, ScheduleJobs
from apps.salts.models import SaltJob,SaltReturn
from settings import MAX_UPLOAD_SIZE
from releaseinfo import SYNDIC_MASTER_FILE_CACHE
import threading
import copy

logger = logging.getLogger("logger_utils")

def format_bytes(num):
    '''
        format bytes
    '''
    if num / 1024.0 / 1024.0 /1024.0 > 1:
        return "%.2f"%(num / 1024.0 / 1024.0 / 1024.0)+'GB'
    if num / 1024.0 / 1024.0 > 1:
        return "%.2f"%(num / 1024.0 / 1024.0)+'MB'
    if num / 1024.0> 1:
        return "%.2f"%(num / 1024.0)+'KB'
    return "%.2f"%(num)+'B'

def sslwrap(func):
    @wraps(func)
    def bar(*args, **kw):
        kw['ssl_version'] = ssl.PROTOCOL_TLSv1
        return func(*args, **kw)
    return bar

def get_sub_dir_name():
    '''
        return sub dir name by date.
        eg: 2015/06/05/
    '''
    now = datetime.datetime.now()
    rel_path = '%s/%02d/%02d/'%(now.year,now.month,now.day)
    return rel_path

def mkdirs(path):
    """
        create folders.
    """
    try:
        if not os.path.exists(path):
            logger.debug("### create file storage dir: %s"%path)
        os.makedirs(path)
    except OSError as exc: # Python >2.5 (except OSError, exc: for Python <2.5)
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
    except:
        logger.error("### folder create fail, please check and retry!")
        raise

def calc_md5(filepath):
    with open(filepath,'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        hash = md5obj.hexdigest()
        return hash

def fileserver_save_file(path,username,md5sum):
    with open(path,"rb") as f:
        files = {'upField':f}
        data = {
            "send_file_username":username,
            "send_file_hash":md5sum
        }
        r = requests.post(FILE_SERVER_HOST,files=files,data=data,verify=False)
        logger.debug("send file response: %s"%r.text)
        if r.status_code == requests.codes.ok:
            res = json.loads(r.text)
            return res.get("result",{}).get("record_id","")

def fileserver_file_exists(md5sum):
    """
        check if the file is on the file server.
    """
    url = FILE_SERVER_HOST + "md5/"+md5sum
    r = requests.get(url,verify=False)
    status_code = r.status_code
    logger.debug("##fileserver_file_exists## url:%s"%(url))
    if status_code not in [200,404]:
        logger.error("BAD RETURN CODE: {0}".format(status_code))
    logger.debug("end fileserver file exist check!")
    return True if r.status_code==200 else False

def fileserver_get_file(tgt,imd5sum,dest,expr_form="list"):
    """
        create folders and get file through cp.get_url.
    """
    parent = os.path.dirname(dest)
    if isinstance(tgt,str):
        tgt = [tgt]
    logger.debug("create parent folder.{0}".format(parent))
    ### should make sure folder exists first.
    send_single_api_request(tgt,"file.mkdir",[parent],expr_form=expr_form)
    status_ok,result = send_single_api_request(tgt,'cp.get_url',[MAPPED_FILE_SERVER_HOST+"md5/"+imd5sum,dest],expr_form=expr_form)
    logger.debug("=== cp.get_url result: {0},{1}".format(status_ok,result))
    return status_ok,result

def save_upload_file(tmp_path,origin_file_name,username,src_ip="",md5sum="",delete=True,location_type=enum_template.UPLOAD_TYPE_LOCAL,remote_path="",remote_account=None):
    """
        save given file to specified folder.
    """
    # store_file_name =  origin_file_name +'_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    store_file_name =  'file_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    upload_record = None
    if not os.path.exists(tmp_path):
        logger.warning("## file not existed,return none, path:%s"%tmp_path)
        return None
    size = os.path.getsize(tmp_path)

    if not md5sum:
        # md5sum = salt.utils.get_hash(tmp_path)
        md5sum = calc_md5(tmp_path)
    logger.debug("## md5 for file %s is %s"%(origin_file_name,md5sum))

    try:
        file_info = FileInfo.objects.get(md5sum=md5sum)
        full_path = REL_FILE_UPLAOD_FOLDER + file_info.path
        if os.path.isfile(full_path):
            if delete:
                logger.debug("## file exists, using existed file, remove temp file.")
                os.remove(tmp_path)
        else:
            logger.debug("## previous file missing, updating file info...")
            rel_dir = get_sub_dir_name()
            store_path = REL_FILE_UPLAOD_FOLDER +rel_dir
            if not os.path.exists(store_path):
                mkdirs(store_path)
            ### shutil.move(tmp_path,store_path+store_file_name)
            # file_info.path=rel_dir+store_file_name
            path = fileserver_save_file(tmp_path,username,md5sum)
            if not path:
                raise Exception("save to fileserver error.")
            file_info.path=path
            if delete: os.remove(tmp_path)
            logger.debug("## old path updated, new path:%s"% file_info.path)
        file_info.save()
    except FileInfo.DoesNotExist:
        rel_dir = get_sub_dir_name()
        store_path = REL_FILE_UPLAOD_FOLDER +rel_dir
        if not os.path.exists(store_path):
            mkdirs(store_path)
        ### shutil.move(tmp_path,store_path+store_file_name)
        # send_file_storage(tmp_path)
        path = fileserver_save_file(tmp_path,username,md5sum)
        if not path:
            raise Exception("save to fileserver error.")
        if delete: os.remove(tmp_path)
        file_info = FileInfo.objects.create(path=path,file_name=origin_file_name,md5sum=md5sum,size=size)
        logger.debug("## new file saved, path:%s"%file_info.path)
    except:
        logger.error("### error save file: %s"%(origin_file_name))
        error = traceback.format_exc()
        logger.error(error)
        print error
        return None

    if file_info:
        upload_record = UploadRecord.objects.create(
            user_name=username,
            fileinfo=file_info,
            file_name=origin_file_name,
            src_ip=src_ip,
            location_type = location_type,
            remote_path = remote_path,
            remote_account = remote_account
        )
    return upload_record


def get_ip_from_request(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        return request.META['HTTP_X_FORWARDED_FOR']
    else:
        return request.META['REMOTE_ADDR']


def format_dst_path(ori_str,src_ip=""):
    """
        format send file path.
    """
    ori_str= str(ori_str).replace(FILESRCIP,src_ip)
    r = re.compile(r"\[DATEFMT:[^]]*\]")
    rep_dict = {}
    now = datetime.datetime.now()
    for i in r.findall(ori_str):
        try:
            fmt = i.replace("[DATEFMT:","").rstrip("]")
            word = now.strftime(fmt)
            rep_dict.update({i:word})
        except:
            print "format not valid"
    for ori,rep in rep_dict.iteritems():
        ori_str = ori_str.replace(ori,rep)
    return ori_str


def send_salt_api_request(params, async=False,uri=""):
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    url = UJOBS_API_HOST + '/api/run/'
    if async:
        url = UJOBS_API_HOST + '/api/run/async'
    if uri:
        url = UJOBS_API_HOST + uri
    logger.debug("### start api request, params:{0}".format(params))
    is_multi = False
    try:
        if isinstance(params, dict):
            params = [params]
        elif isinstance(params, list):
            is_multi = True
        else:
            raise Exception('params should be a json list or dict')
        for param in params:
            param['username'] = SALT_MASTER_USER
            param['password'] = SALT_MASTER_PASSWD
        ssl.wrap_socket = sslwrap(ssl.wrap_socket)
        resp = requests.post(url,
                             data=json.dumps(params,ensure_ascii=False),
                             headers=header,
                             verify=False,
                             )
        code = resp.status_code
        if code == requests.codes.ok:
            result = resp.json()
            if result['status'] == 200:
                result = result["result"]["return"]
                result = result if is_multi else result[0]
            else:
                logger.debug("error_result:{0}".format(result))
                raise Exception(result['result'])
        else:
            result = requests.status_codes._codes.get(code)
            return False, result
    except Exception, e:
        error = traceback.format_exc()
        logger.error("api call failed,error:{0}".format(e.message))
        logger.error(error)
        print error
        return False, e.message
    logger.debug("### end api request.")
    return True, result

def get_master_addrs():
    status_ok, result = send_salt_api_request({},uri="/api/master_addrs/")
    if not status_ok:
        return None
    return result["master_addrs"]


def send_single_api_request(tgt, fun, arg=[], expr_form="", async=False, uri="", timeout=0,kwarg={}):
    kwarg = copy.deepcopy(kwarg)
    params = {
        "tgt": tgt,
        "fun": fun,
        "arg": arg
    }
    if expr_form:
        params['expr_form'] = expr_form
    # reset_system_locale TO False to solve locale problem.
    if fun in ['cmd.script','cmd.run']:
        kwarg.update({'reset_system_locale':False})
    else:
        if 'reset_system_locale' in kwarg.keys():
            del kwarg['reset_system_locale']
    if kwarg:
        params['kwarg'] = kwarg
    if timeout and isinstance(timeout,int):
        params['timeout'] = timeout
    status,result = send_salt_api_request(dict(params), async=async, uri=uri)
    if not isinstance(result,dict):
        status = False
        logger.warning("### api call return non dict format,info: {0}".format(json.dumps(result)))
        result = {}
    if async and status:
        result = result.get("jid","")
    return status,result

def send_runner_api_request(fun,**kwargs):
    """
        send runner api call.
    """
    params = {'fun':fun}
    params.update(kwargs)
    logger.debug("start runner api call")
    status,result = send_salt_api_request(params)
    logger.debug("end runner api call, status:{0}".format(status))
    if not status:
        logger.debug("return result:{0}".format(result))
    return status,result

def get_input_ips(ips_json):
    """
        get ip dict from hidden input area.
    """
    # return set(['117.121.19.137'])
    ip_set = set()
    if ips_json:
        ips_dict=json.loads(ips_json)
        for (item, minion_info) in ips_dict.items():
            if item == 'total' or item == 'num':
                continue
            ip_str = minion_info[3]
            ip_list = ip_str.split('<br>')
            minion_ip = ip_list[0]
            ip_set.add(minion_ip)
    return ip_set

def build_hidden_ip_dict(target_ips):
#    minions_ups = rc.smembers(MINIONS_UP_SET_KEY)
#    hide_ip_dict = {}
#    num = 0
#    for minion_ip in target_ips:
#        minion_psw_new = ''
#        minion_os = ''
#        if not rc.exists(IP_KEY_PREFIX+minion_ip):
#            hide_ip_dict[minion_ip] = [-99, minion_psw_new, minion_os]
#            continue
#        minion_id = rc.get(IP_KEY_PREFIX+minion_ip)
#        minion_os = rc.hget(DETAIL_KEY_PREFIX+minion_id,'kernel')
#        status = 1 if minion_id in minions_ups else -1
#        hide_ip_dict[minion_ip]=[status,"",minion_os]
#        num = num + 1 if status == 1 else num
#
#    hide_ip_dict['num'] = num
#    hide_ip_dict['total'] = len(target_ips)
#    return hide_ip_dict
    
    minions_ups = rc.smembers(MINIONS_UP_SET_KEY)
    hide_ip_dict = {}
    num = 0
    for minion_ip in target_ips:
        minion_psw_new = ''
        minion_os = ''
        if not rc.exists(IP_KEY_PREFIX+minion_ip):
            hide_ip_dict[minion_ip] = [-99, minion_psw_new, minion_os, minion_ip]
            continue
        minion_id = rc.get(IP_KEY_PREFIX+minion_ip)
        minion_os = rc.hget(DETAIL_KEY_PREFIX+minion_id,'kernel')
        status = 1 if minion_id in minions_ups else -1
        hide_ip_dict[minion_id]=[status, "", minion_os, minion_ip]
        num = num + 1 if status == 1 else num

    hide_ip_dict['num'] = num
    hide_ip_dict['total'] = len(target_ips)
    return hide_ip_dict


def get_job_result(jid,timeout=30,history_step=None,check_active=True,total=0):
    '''
        get job result using jid, return salt return from db as a dict.
        default timeout is 30 min.
    '''
    ret_dict = {}
    start = datetime.datetime.now()
    logger.debug("Start get job result for jid: {0}".format(jid))
    if history_step: RunningResult.objects.create(step=history_step,content=u"开始获取执行结果,超时设置{0}分".format(timeout))
    while datetime.datetime.now() - start < datetime.timedelta(minutes=timeout):
        status,result = False,{}

        if SaltReturn.objects.filter(jid=jid).count() == total:
            logger.debug("Result already in DB, abort jobs.active")
        elif check_active:
            ## check if job is active
            retry = 0
            while not status and retry < 3:
                retry += 1
                if history_step: RunningResult.objects.create(step=history_step,content=u"==开始获取当前正在执行作业列表")
                status,result = send_runner_api_request(fun='jobs.active')
                logger.debug("## result of jobs.active: {0}".format(result))
                if status and result and isinstance(result,dict):
                    logger.debug("Active job keys:{0}".format(",".join(result.keys())))
                    break
                time.sleep(3)

            if not isinstance(result,dict):
                logger.debug('jobs.active return format error')
                if history_step: RunningResult.objects.create(step=history_step,content=u"返回结果格式错误, 重试获取中...")
                time.sleep(5)
                if "KeyError" in result:
                    logger.debug("salt runtime error.")
                    # break
                # continue
            else:
                if str(jid) in result.keys():
                    logger.debug("Jid:{0} is still active".format(jid))
                    if history_step: RunningResult.objects.create(step=history_step,content=u"作业执行中,稍候重试获取...")
                    time.sleep(3)
                    continue

        ## get db results, faster than call salt-api.
        # if history_step: RunningResult.objects.create(step=history_step,content=u"作业执行结束,开始获取返回结果")
        logger.debug("start get results from db....")
        salt_returns = SaltReturn.objects.filter(jid=jid)
        num_return = salt_returns.count()
        if num_return == 0:
            if history_step: RunningResult.objects.create(step=history_step, content=u"数据库中未找到执行结果, 开始获取salt原始结果")
            logger.debug("No salt return found in db, using jobs.lookup_jid to find result.")
            status, result = send_runner_api_request(fun='jobs.lookup_jid', jid=jid)
            logger.debug("Result found: {0}".format(result))
            if status and result and isinstance(result,dict):
                ret_dict = result
                break
            else:
                if history_step: RunningResult.objects.create(step=history_step, content=u"返回结果失败")
        else:
            count = 0
            while count < 12 * 2:
                if history_step: RunningResult.objects.create(step=history_step, content=u"当前返回结果数:{0}/{1}".format(num_return,total))
                if num_return == total:
                    break
                count+=1
                time.sleep(5)
                salt_returns = SaltReturn.objects.filter(jid=jid)
                num_return = salt_returns.count()
            [ret_dict.update({item.minion_id: json.loads(item.result)}) for item in salt_returns]
            if num_return == total:
                break
    if datetime.datetime.now() - start > datetime.timedelta(minutes=timeout):
        logger.debug("Timeout get job result for jid:{0}".format(jid))
        if history_step: RunningResult.objects.create(step=history_step,content=u"获取结果超时")
    logger.debug("End get job result.")
    if history_step: RunningResult.objects.create(step=history_step,content=u"获取执行返回结果结束")
    return ret_dict


def get_salt_returns_by_jid(jid, total, retry=12 * 2):
    count = 1
    salt_returns = []
    ret_dict = {}
    try:
        while count < retry:
            logger.debug("==> start get salt returns by id:{0}, round:{1}".format(jid, count))
            count += 1
            salt_returns = SaltReturn.objects.filter(jid=jid)
            num_return = salt_returns.count()
            logger.debug("==> current db results: {0}/{1}".format(num_return, total))
            if num_return == total:
                break
            time.sleep(5)
        [ret_dict.update({item.minion_id: json.loads(item.result)}) for item in salt_returns]
    except Exception,e:
        logger.error(traceback.format_exc())
        ret_dict = {}
    return ret_dict

def handle_step_script(history_step):
    '''
         执行脚本
    '''
    history = history_step.history
    history_step.start_time = datetime.datetime.now()
    history_step.result = enum_history.RESULT_PROCESSING #正在执行中
    history_step.save()

    code = 200

    history_step_script = _history.get_historyStepScript_by_params(step=history_step)
    if not history_step_script:
        logger.error(" no script info found for history_step, his_id:{0}".format(history_step.id))
        return {
            "status":500,
            "result":{
                "msg": u"获取执行脚本信息失败"
            }
        }
        
    # 等待执行的minion集合.
    ip_set = set(json.loads(history.target) if history.target else [])
    # ip_set = set(["117.121.19.137","117.121.19.131"])
    account = history.account
    if history_step.is_setting:# 步骤设定为空时使用全程设定IP
        ip_set = set(json.loads(history_step.target) if history_step.target and eval(history_step.target) else ip_set)
        account = history_step.account

    version = history_step_script.version
    script = version.script
    file_doc_num = version.id % 100
    file_doc_path = os.path.join(MEDIA_ROOT,'scripts','%s'%file_doc_num)
    suffix = enum_script.SCIPT_TYPE_DICT.get(int(script.script_type))
    filename = u'%s.%s'%(version.name, suffix)
    file_path = os.path.join(file_doc_path,filename)
    md5sum = calc_md5(file_path)
    
    timeout = history_step_script.timeout
    if timeout:
        timeout = int(timeout)
    else:
        timeout = 0
    parameter = history_step_script.parameter

    kwarg = {}
    if timeout:
        kwarg['timeout'] = timeout
    if parameter:
        kwarg['args'] = parameter
    
    try:
        RunningResult.objects.create(step=history_step,content=u"开始预处理目标机器",progress=5)
        # minion-ip map
        minion_id_map = {}

        # add all minion item to ip_set.
        ip_set_win = set()
        ip_set_linux = set()
        sub_master_set = set()
        logger.debug("before redis call")
        for item in ip_set:
            logger.debug("{0}, {1}".format(item,IP_KEY_PREFIX+item))
            minion_id = rc.get(IP_KEY_PREFIX+item)
            if minion_id in minion_id_map.keys():
                continue
            minion_id_map.update({minion_id:item})
            ip_set.add(item)
            redis_info = rc.hmget(DETAIL_KEY_PREFIX+minion_id,'kernel','master')
            minion_os = redis_info[0]
            syndic_id = redis_info[1]
            if minion_os.lower().startswith('win'):
                ip_set_win.add(item)
            else:
                ip_set_linux.add(item)
            sub_master_set.add(syndic_id)
        logger.debug("redis handle end...")

        logger.debug("after redis call")
        if len(ip_set)==0:
            history_step.end_time = datetime.datetime.now()
            history_step.delta_time = (history_step.end_time - history_step.start_time).seconds
            history_step.result = enum_history.RESULT_FAIL
            history_step.save()
        
            content = u"可操作目标机器为空"
            RunningResult.objects.create(step=history_step,content=content,progress=100)
        
            code = 500
            return {"status":code}
    
        fail_ips_set = set()
        logger.debug("# start check online agent status...")
        RunningResult.objects.create(step=history_step,content=u"开始获取当前agent状态",progress=10)
        id_list = list(set([rc.get(IP_KEY_PREFIX+ip) for ip in ip_set]))
        history_step.total_ips = json.dumps(list(ip_set))
        history_step.save()
    
        online_agents_num,offline_agents_num,online_agents,offline_agents = get_online_status(id_list)
        
        logger.debug("online:%s,offline:%s"%(list(online_agents),list(offline_agents)))
        logger.debug("# check finished, online_num:%s,offline_num:%s.details,"%(online_agents_num,offline_agents_num))
        RunningResult.objects.create(step=history_step,content=u"检查结果,在线:%s,离线:%s"%
                                                               ([minion_id_map.get(id) for id in online_agents],
                                                               [minion_id_map.get(id) for id in offline_agents]),progress=20)
        #去除离线agent
        if offline_agents:
            for offline_ip in list(offline_agents):
                RunningResult.objects.create(ip=offline_ip,step=history_step,content=u"agent状态离线，脚本未执行",progress=25)
                if offline_ip in list(ip_set_win):
                    ip_set_win.remove(offline_ip)
                if offline_ip in list(ip_set_linux):
                    ip_set_linux.remove(offline_ip)
        
        history_step.total_ips = json.dumps([minion_id_map.get(id) for id in list(id_list)])
        history_step.abnormal_ips = json.dumps([minion_id_map.get(id) for id in list(offline_agents)])
        history_step.save()
    
        RunningResult.objects.create(step=history_step,content=u"开始预处理脚本文件",progress=30)
        minion_path = '/srv/salt/scripts/%s/'%file_doc_num
        minion_file = '%s%s'%(minion_path,filename)
    
    #        send_single_api_request(sub_masters, 'file.mkdir', [minion_path], expr_form='list')
        fileserver_get_file(list(sub_master_set),md5sum,minion_file,expr_form="list")
    #        send_single_api_request(sub_masters, 'cp.get_file', ['salt://scripts/%s/%s'%(file_doc_num,filename),minion_file], expr_form='list')

        salt_script_name = 'salt://scripts/%s/%s'%(file_doc_num,filename)
        cache_retry = 1
        fail_set = set([minion_id_map.get(id) for id in online_agents])
        success_set = set()
        RunningResult.objects.create(step=history_step,content=u"开始客户端缓存脚本文件")
        while cache_retry < 4 and len(fail_set)>0:
            logger.debug("start {0} cache file for dst minion...".format(cache_retry))
            RunningResult.objects.create(step=history_step,content=u"开始第{0}次缓存脚本, 目标:{1}".format(cache_retry,','.join(fail_set)))
            cache_targets= 'S@' + ' or S@'.join(fail_set)
            _, cache_result = send_single_api_request(cache_targets, 'cp.cache_file', [salt_script_name], expr_form='compound')

            # 增加异步执行
            jid=None
            count = 0
            while True:
                if count==100:
                    break
                try:
                    logger.debug("start async cache_file...")
                    _, jid = send_single_api_request(cache_targets,"cp.cache_file", [salt_script_name],expr_form="compound",async=True)
                    jid = int(jid)
                    break
                except Exception,e:
                    error = traceback.format_exc()
                    print error
                    time.sleep(3)
                    logger.error(error)
                    logger.debug("jid invalid:{0}".format(jid))
                count+=1
            time.sleep(5)
            async_cache_result = {}
            if count <100:
                logger.debug("### start async cache file, jid:{0}".format(jid))
                async_cache_result = get_salt_returns_by_jid(jid,len(fail_set))

            for key in fail_set:
                res = cache_result.get(rc.get(IP_KEY_PREFIX+key),'') or async_cache_result.get(rc.get(IP_KEY_PREFIX+key),'')
                logger.debug("### cache result for {0}: {1}".format(key,res))
                if res:
                    success_set.add(key)
            fail_set = fail_set.difference(success_set)
            if len(fail_set) > 0:
                RunningResult.objects.create(step=history_step,content=u"{0}缓存脚本失败".format(','.join(fail_set)))
            cache_retry += 1
            time.sleep(1)
        logger.debug("cache file for cmd.script end, failed cache minions_num: {0}".format(len(fail_set)))
        for item in fail_set:
            RunningResult.objects.create(ip=item,step=history_step,content=u"缓存脚本文件失败")
        RunningResult.objects.create(step=history_step,content=u"客户端缓存脚本文件结束")
        # if cache_retry == 4:
        #     RunningResult.objects.create(step=history_step,content=u"minion获取脚本文件失败,脚本未执行,请稍候再试")
        #     raise Exception, u"minion获取脚本文件失败"
        ip_set_win = ip_set_win.intersection(success_set)

        tmp_fails = set()
        tmp_succeeds = set()

        # 当前已返回结果的IP, 避免结果记录重复.
        cur_res_ip_set = set()
        if ip_set_win:
            total_win = len(list(ip_set_win))
            try:
                RunningResult.objects.create(step=history_step,content=u"windows机器开始执行脚本",progress=40)
                if script.script_type == 1:
                    fail_ips_set = fail_ips_set | ip_set_win
                    index = 0
                    for minion_ip in list(ip_set_win):
                        index += 1
                        tmp_fails.add(minion_ip)
                        RunningResult.objects.create(ip=minion_ip,step=history_step,content=u"windows不支持shell脚本",progress=50)
                else:
                    target_ips_win = 'S@' + ' or S@'.join(list(ip_set_win))
                    salt_script_name = 'salt://scripts/%s/%s'%(file_doc_num,filename)
                    publish_time = datetime.datetime.now()
                    _,result_dict_win = send_single_api_request(target_ips_win, 'cmd.script', [salt_script_name], kwarg=dict(kwarg), expr_form='compound')
                    index = 0
                    jids = SaltJob.objects.filter(load__contains=version.name).filter(ctime__gte=publish_time).filter(load__contains='cmd.script')\
                        .filter(load__contains='eauth').order_by('id')
                    jid_obj = jids[0] if jids.count()>0 else None
                    if jid_obj:
                        RunningResult.objects.create(step=history_step,content="jid for windows: {0}, time: {1}".format(jid_obj.jid,jid_obj.ctime))
                    else:
                        RunningResult.objects.create(step=history_step,content=u"jid for windows 未找到")

                    if len(ip_set_win)>len(result_dict_win) and jid_obj:
                        logger.debug("result not complete, start result collect process....")
                        result_dict_win = get_salt_returns_by_jid(jid_obj.jid,len(ip_set_win),retry=3) or result_dict_win

                    if not isinstance(result_dict_win,dict):
                        logger.error("salt-api return is not a dict, {0}".format(json.dumps(result_dict_win)))
                        result_dict_win={}

                    #将返回结果先进行输出.
                    for key,value in result_dict_win.iteritems():
                        key = minion_id_map.get(key,key)
                        if value and isinstance(value,dict):
                            stderr = value.get("stderr","")
                            stdout = value.get("stdout","")
                            pid = value.get('pid',0)
                            cur_res_ip_set.add(key)
                            if stderr or not pid:
                                fail_msg = stderr if stderr else json.dumps(value)
                                RunningResult.objects.create(ip=key,step=history_step,content=u"执行失败, 结果返回如下:\n"+fail_msg)
                                tmp_fails.add(key)
                                fail_ips_set.add(key)
                                continue
                            if stdout and 'Timed out' in stdout:
                                RunningResult.objects.create(ip=key,step=history_step,content="\n"+stdout)
                                tmp_fails.add(key)
                                fail_ips_set.add(key)
                                continue
                            if pid and not stderr:
                                tmp_succeeds.add(key)
                                RunningResult.objects.create(ip=key,step=history_step,content="\n"+stdout)
                    history_step.success_ips = json.dumps(list(tmp_succeeds))
                    history_step.fail_ips = json.dumps(list(tmp_fails))
                    history_step.save()

                    if len(ip_set_win) > len(result_dict_win) and jid_obj:
                        RunningResult.objects.create(step=history_step,content=u"当前执行结果返回 {0}/{1} 条".format(len(result_dict_win),len(ip_set_win)))
                        logger.debug("result not complete, start result collect process, return:{0}/{1}".format(len(result_dict_win),len(ip_set_win)))
                        result_dict_win.update(get_job_result(jid_obj.jid,history_step=history_step,total=len(ip_set_win)))

                    RunningResult.objects.create(step=history_step,content=u"执行结果返回 {0}/{1} 条".format(len(result_dict_win),len(ip_set_win)))

                    for result_ip in ip_set_win:
                        index += 1
                        result_id = rc.get(IP_KEY_PREFIX+result_ip)
                        result_value = result_dict_win.get(result_id,None)

                        # 已经返回结果的IP不再进行处理
                        if result_ip in cur_res_ip_set:
                            logger.debug("result already get for ip:{0}".format(result_ip))
                            continue
                        cur_res_ip_set.add(result_ip)

                        if isinstance(result_value,dict):
                            stderr = result_value.get('stderr')
                            stdout = result_value.get('stdout')
                            pid = result_value.get('pid',0)
                            if stderr or not pid:
                                fail_msg = stderr if stderr else json.dumps(result_value)
                                RunningResult.objects.create(ip=result_ip,step=history_step,content=u"执行失败, 结果返回如下:\n"+fail_msg)
                                fail_ips_set.add(result_ip)
                            elif 'Timed out' in stdout:
                                RunningResult.objects.create(ip=result_ip,step=history_step,content="\n"+stdout)
                                fail_ips_set.add(result_ip)
                            else:
                                RunningResult.objects.create(ip=result_ip,step=history_step,content="\n"+stdout)

                        else:
                            RunningResult.objects.create(ip=result_ip,step=history_step,content=result_value or u"salt未返回结果")
                            fail_ips_set.add(result_ip)
            except Exception,e:
                error = traceback.format_exc()
                logger.error('#### execute win script fail! info: %s'%(error))
                fail_ips_set = ip_set_win
                index = 0
                for minion_ip in list(ip_set_win):
                    index += 1
                    RunningResult.objects.create(ip=minion_ip,step=history_step,content='%s'%e)
            RunningResult.objects.create(step=history_step,content=u"windows机器执行脚本结束",progress=60)

        ip_set_linux = ip_set_linux.intersection(success_set)

        if ip_set_linux:
            kwarg['runas'] = account.name
            total_linux = len(list(ip_set_linux))
            try:
                RunningResult.objects.create(step=history_step,content=u"linux机器开始执行脚本",progress=70)
                target_ips_linux = 'S@' + ' or S@'.join(list(ip_set_linux))
                salt_script_name = 'salt://scripts/%s/%s'%(file_doc_num,filename)
                publish_time = datetime.datetime.now()
                _,result_dict_linux = send_single_api_request(target_ips_linux, 'cmd.script', [salt_script_name], kwarg=dict(kwarg), expr_form='compound')
                index = 0
                logger.debug(result_dict_linux)
                jids = SaltJob.objects.filter(load__contains=version.name).filter(ctime__gte=publish_time).filter(load__contains='cmd.script')\
                    .filter(load__contains='eauth').order_by('id')
                jid_obj = jids[0] if jids.count()>0 else None
                if jid_obj:
                    RunningResult.objects.create(step=history_step,content="jid for linux: {0}, time: {1}".format(jid_obj.jid,jid_obj.ctime))
                else:
                    RunningResult.objects.create(step=history_step,content=u"jid for linux 未找到")

                if len(ip_set_linux)>len(result_dict_linux) and jid_obj:
                    logger.debug("result not complete, start result collect process....")
                    result_dict_linux = get_salt_returns_by_jid(jid_obj.jid,len(ip_set_linux),retry=3) or result_dict_linux

                if not isinstance(result_dict_linux,dict):
                    logger.error("salt-api return is not a dict, {0}".format(json.dumps(result_dict_linux)))
                    result_dict_linux={}

                #将返回结果先进行输出.
                for key,value in result_dict_linux.iteritems():
                    key = minion_id_map.get(key,key)
                    if value and isinstance(value,dict):
                        stderr = value.get("stderr","")
                        stdout = value.get("stdout","")
                        pid = value.get('pid',0)

                        cur_res_ip_set.add(key)

                        if stderr or not pid:
                            fail_msg = stderr if stderr else json.dumps(value)
                            RunningResult.objects.create(ip=key,step=history_step,content=u"执行失败, 结果返回如下:\n"+fail_msg)
                            tmp_fails.add(key)
                            fail_ips_set.add(key)
                            continue
                        if stdout and 'Timed out' in stdout:
                            RunningResult.objects.create(ip=key,step=history_step,content="\n"+stdout)
                            tmp_fails.add(key)
                            fail_ips_set.add(key)
                            continue
                        if pid and not stderr:
                            tmp_succeeds.add(key)
                            RunningResult.objects.create(ip=key,step=history_step,content="\n"+stdout)
                history_step.success_ips = json.dumps(list(tmp_succeeds))
                history_step.fail_ips = json.dumps(list(tmp_fails))
                history_step.save()

                if len(ip_set_linux) > len(result_dict_linux) and jid_obj:
                    RunningResult.objects.create(step=history_step,content=u"当前执行结果返回 {0}/{1} 条".format(len(result_dict_linux),len(ip_set_linux)))
                    logger.debug("result not complete, start result collect process, return:{0}/{1}".format(len(result_dict_linux),len(ip_set_linux)))
                    result_dict_linux.update(get_job_result(jid_obj.jid,history_step=history_step,total=len(ip_set_linux)))#####

                RunningResult.objects.create(step=history_step,content=u"执行结果返回 {0}/{1} 条".format(len(result_dict_linux),len(ip_set_linux)))

                for result_ip in ip_set_linux:
                    index += 1
                    result_id = rc.get(IP_KEY_PREFIX+result_ip)
                    result_value = result_dict_linux.get(result_id,None)

                    # 已经返回结果的IP不再进行处理
                    if result_ip in cur_res_ip_set:
                        logger.debug("result already get for ip:{0}".format(result_ip))
                        continue
                    cur_res_ip_set.add(result_ip)

                    if isinstance(result_value,dict):
                        stderr = result_value.get('stderr','')
                        stdout = result_value.get('stdout','')
                        pid = result_value.get('pid',0)
                        # 返回{}的情况
                        if not result_value:
                            RunningResult.objects.create(ip=result_ip,step=history_step,content=u"salt返回结果为空\n{0}".format(json.dumps(result_value)))
                            fail_ips_set.add(result_ip)
                            continue
                        if stderr or not pid:
                            fail_msg = stderr if stderr else json.dumps(result_value)
                            RunningResult.objects.create(ip=result_ip,step=history_step,content=u"执行失败, 结果返回如下:\n"+fail_msg)
                            fail_ips_set.add(result_ip)
                        elif stdout and 'Timed out' in stdout:
                            RunningResult.objects.create(ip=result_ip,step=history_step,content="\n"+stdout)
                            fail_ips_set.add(result_ip)
                        else:
                            RunningResult.objects.create(ip=result_ip,step=history_step,content="\n"+stdout)
                    else:
                        RunningResult.objects.create(ip=result_ip,step=history_step,content=result_value or u"salt未返回结果")
                        fail_ips_set.add(result_ip)

                RunningResult.objects.create(step=history_step,content=u"linux机器执行脚本结束",progress=100)
            except Exception,e:
                error = traceback.format_exc()
                logger.error('#### execute linux script fail! info: %s'%(error))
                fail_ips_set = ip_set_linux
                index = 0
                for minion_ip in list(ip_set_linux):
                    index += 1
                    RunningResult.objects.create(ip=minion_ip,step=history_step,content='%s'%error,progress=(70+30/total_linux*index))
                RunningResult.objects.create(step=history_step,content=u"linux机器执行脚本结束",progress=100)
        RunningResult.objects.create(step=history_step,content=u"脚本执行结束",progress=100)

        [fail_ips_set.add(ip) for ip in fail_set]

        if len(fail_ips_set)>0 or offline_agents_num>0:
            code = 500
            history_step.result = enum_history.RESULT_FAIL
            history_step.fail_ips = json.dumps(list(fail_ips_set))
        else:
            history_step.result = enum_history.RESULT_SUCCESS

        history_step.end_time = datetime.datetime.now()
        history_step.delta_time = (history_step.end_time - history_step.start_time).seconds
        history_step.success_ips = json.dumps(list(ip_set.difference(fail_ips_set).difference(offline_agents)))
        history_step.save()

    except Exception,e:
        print e
        code = 500
        history_step.end_time = datetime.datetime.now()
        history_step.delta_time = (history_step.end_time - history_step.start_time).seconds
        history_step.result = enum_history.RESULT_FAIL
        history_step.fail_ips = json.dumps(list(ip_set))
        history_step.save()

        error = traceback.format_exc()
        logger.error('#### execute script fail! info: %s'%(error))
        RunningResult.objects.create(ip='*',step=history_step,content='error',progress=100)

    return {"status":code}


def handle_step_push_file(history_step):
    '''
        handle send file.
    '''
    history = history_step.history
    history_step.start_time = datetime.datetime.now()
    history_step.result = enum_history.RESULT_PROCESSING #正在执行中
    history_step.save()

    status = 200
    user_name = history_step.history.user.username

    remote_file_records = HistoryFileInfo.objects.filter(step=history_step,location_type=enum_template.UPLOAD_TYPE_REMOTE)
    local_file_records = HistoryFileInfo.objects.filter(step=history_step,location_type=enum_template.UPLOAD_TYPE_LOCAL)

    src_paths = set()

    # final return result.
    minion_result = {}

    history_step_push_file = _history.get_historyStepPushFile_by_params(step=history_step)
    if not history_step_push_file:
        logger.error(" no push file info found for history_step, his_id:{0}".format(history_step.id))
        return {
            "status":500,
            "result":{
                "msg": u"获取文件分发信息失败"
            }
        }
    
    speed = history_step_push_file.limit
    target_path = os.path.normpath(str(history_step_push_file.push_to)).replace("\\","/")

    # 等待拉取的minion集合.
    ip_set = set(json.loads(history.target) if history.target else [])
    if history_step.is_setting:
        ip_set = set(json.loads(history_step.target) if history_step.target and eval(history_step.target) else ip_set)

    history_step.total_ips = json.dumps(list(ip_set))
    history_step.save()
    local_ips = get_master_addrs()

    # minion-ip map
    minion_id_map = {}


    # failed path-state map
    fail_transfer_items = {}

    RunningResult.objects.create(step=history_step,content=u"开始检查目标机器",progress=3)

    # get syndics which need to transfer files.
    syndics = set()
    # master_id = salt.utils.network.generate_minion_id()
    # all failed ips
    fail_ids_set = set()
    logger.debug("=== start check syndic and ips ...")
    dup_ips = set()
    for ip in ip_set:
        minion_id = rc.get(IP_KEY_PREFIX+ip)
        if minion_id in minion_id_map.keys():
            RunningResult.objects.create(step=history_step,ip=ip,content=u"目标机器IP%s与本IP属同一台机器,跳过处理."%(ip),progress=5)
            logger.warning("IP %s has dup in minion ip_set:%s"%(ip,minion_id_map.get(minion_id)))
            dup_ips.add(ip)
            continue
        minion_id_map.update({minion_id:ip})
        if minion_id and rc.hexists(DETAIL_KEY_PREFIX+minion_id,'master'):
            syndic = rc.hget(DETAIL_KEY_PREFIX+minion_id,'master')
            if syndic and syndic not in local_ips:
                syndics.add(syndic)
        else:
            # remove invalid ip from ip set.
            logger.warning("## ip invalid, remove ip:%s"%ip)
            content = u'未找到该目标机器信息,分发失败'
            RunningResult.objects.create(step=history_step,ip=ip,content=content,progress=5)
            minion_result.update({ip:{
                'state':'fail',
                'msg': content
            }})
            fail_ids_set.add(ip)

    ip_set = ip_set.difference(fail_ids_set,dup_ips)
    logger.debug("valid ip_set:%s"%ip_set)
    if len(ip_set)==0:
        history_step.end_time = datetime.datetime.now()
        history_step.delta_time = (history_step.end_time - history_step.start_time).seconds
        history_step.result = enum_history.RESULT_FAIL
        history_step.save()

        RunningResult.objects.create(step=history_step,content=u"可操作目标机器不能为空",progress=100)
        return {
            "status":500,
            "result":{
                "msg": u"可操作目标机器不能为空"
            }
        }
    RunningResult.objects.create(step=history_step,content=u"目标机器检查完成",progress=8)
    logger.debug("=== end check, syndics:%s,invalid_ips:%s"%(syndics,fail_ids_set))

    # get current input agent stasus.
    logger.debug("# start check online agent status")
    RunningResult.objects.create(step=history_step,content=u"开始获取当前agent状态",progress=9)
    id_list = list(set([rc.get(IP_KEY_PREFIX+ip) for ip in ip_set]))

    #### get online status from cache.
    cached_up_agents = rc.smembers(MINIONS_UP_SET_KEY)
    online_agents = set(cached_up_agents).intersection(set(id_list))
    online_agents_num = len(online_agents)
    offline_agents_num = len(id_list)-online_agents_num
    offline_agents = set(id_list).difference(online_agents)
    logger.debug("online:%s,offline:%s"%(list(online_agents),list(offline_agents)))
    logger.debug("# check finished, online_num:%s,offline_num:%s.details,"%(online_agents_num,offline_agents_num))
    RunningResult.objects.create(step=history_step,content=u"检查结果,在线:%s,离线:%s"%
                                                           ([minion_id_map.get(id) for id in online_agents],
                                                            [minion_id_map.get(id) for id in offline_agents]),progress=12)

    history_step.total_ips = json.dumps([minion_id_map.get(id) for id in list(id_list)])
    history_step.abnormal_ips = json.dumps([minion_id_map.get(id) for id in list(offline_agents)])
    history_step.save()
    RunningResult.objects.create(step=history_step,content=u"获取所有agent状态结束",progress=13)
    for offline_agent in offline_agents:
        RunningResult.objects.create(ip=minion_id_map.get(offline_agent),step=history_step,content=u"分发时agent离线,分发失败",progress=14)

    fail_ids_set = set()
    remote_file_records_length = remote_file_records.count()
    if remote_file_records_length > 0:
        logger.debug("========= start transfer remote src files to master ==========")
        # RunningResult.objects.create(step=history_step,content=u"开始拉取文件到master")
        RunningResult.objects.create(step=history_step,content=u" 开始预处理所有远程文件  ",progress=15)
        progress = 15
        for item in remote_file_records:
            start = progress
            part = int(20/remote_file_records_length)
            path = item.remote_path
            remote_ip = str(item.remote_ip)
            input_path = path
            path = os.path.normpath(path.replace('\\','/'))
            try:
#                remote_account_id = item.push_account.id

                # pull file from src ip to master.
                remote_minion_id = rc.get(IP_KEY_PREFIX+remote_ip)
                RunningResult.objects.create(step=history_step,content=u"开始处理%s上的远程文件:%s"%(remote_ip,input_path),progress=progress)
                progress+= part
                logger.debug("## start handle remote src path:%s"%(path))
                minion_id_map.update({remote_minion_id:remote_ip})

                # if source file is on the master, just save it.
                if remote_ip in local_ips:
                    RunningResult.objects.create(step=history_step,content=u"检查到该文件为master上文件")
                    if not os.path.exists(path):
                        logger.error("## local file not exist, skip path:%s"%(path))
                        fail_ids_set = set(online_agents)
                        fail_transfer_items.update({
                            input_path:{
                                'state':'fail',
                                'msg':u'文件未找到'
                        }})
                        RunningResult.objects.create(step=history_step,content=u"文件不存在,跳过处理")
                        continue
                    file_size = os.path.getsize(path)/1024.0/1024.0
                    if file_size > MAX_UPLOAD_SIZE:
                        logger.warning("file too large, skip transfer!")
                        content = u'文件大小大于%sM,实际大小:%2fM,跳过处理.'%(MAX_UPLOAD_SIZE,file_size)
                        RunningResult.objects.create(step=history_step,content=content)
                        fail_transfer_items.update({
                            input_path:{
                                'state':'fail',
                                'msg': content
                            }})
                        continue
                    # md5sum = salt.utils.get_hash(path)
                    ##### if file is on master, using requests to send it to fileserver.
                    record = save_upload_file(path,os.path.basename(path),user_name,delete=False,src_ip=remote_ip)
                    if record:
                        # record_ids.append(str(record.id))
                        src_paths.add((record.pk,input_path))
                        RunningResult.objects.create(step=history_step,content=u"文件保存成功,record id:%s"%(record.id))
                        logger.debug("### local file save ok, record is %s"%(record.id))
                    else:
                        fail_ids_set = set(online_agents)
                        logger.error("### local file save failed, path:%s"%(path))
                        RunningResult.objects.create(step=history_step,content=u"保存文件记录失败!")
                        fail_transfer_items.update({
                            input_path:{
                                'state':'fail',
                                'msg':u'保存文件至master失败'
                            }})
                    continue
                md5sum = ""
                record = None
                try:
                    # check if remote file exists.
                    logger.debug("### start handle remote file: %s"%path)
                    # check_cmd= client.cmd(remote_minion_id,'file.get_sum',[path,'md5'])
                    status_ok,check_cmd=send_single_api_request(remote_minion_id,'file.get_sum',[path,'md5'])
                    md5sum = check_cmd.get(remote_minion_id,"")
                    if md5sum == "File not found":
                        fail_ids_set = set(online_agents)
                        RunningResult.objects.create(step=history_step,content=u"ERROR: 远程文件不存在,%s"%(input_path))
                        logger.warning("### remote source file not found:%s"%path)
                        fail_transfer_items.update({
                            input_path:{
                                'state':'fail',
                                'msg':u'远程文件未找到'
                            }})
                        continue
                    logger.debug("md5 of remote source file:%s"%(md5sum))
                    # RunningResult.objects.create(step=history_step,content=u"文件md5:%s"%(md5sum))
                    # get size of file.
                    logger.debug("## start check file size...")
                    # size_cmd = client.cmd(remote_minion_id,'file.lstat',[path])
                    status_ok,size_cmd = send_single_api_request(remote_minion_id,'file.lstat',[path])
                    file_size = size_cmd.get(remote_minion_id,{}).get('st_size',-1)
                    if file_size ==-1:
                        logger.warning("### get file size fail,res:%s"%size_cmd)
                        fail_transfer_items.update({
                            input_path:{
                                'state':'fail',
                                'msg':u'获取文件大小失败'
                            }})
                        continue
                    file_size = file_size/1024.0/1024.0
                    if file_size > MAX_UPLOAD_SIZE:
                        logger.warning("## file larger than %s M, actual size is:%2fM"%(MAX_UPLOAD_SIZE,file_size))
                        RunningResult.objects.create(step=history_step,content=u'远程文件大于%sM,实际大小%2fM'%(MAX_UPLOAD_SIZE,file_size))
                        fail_transfer_items.update({
                            input_path:{
                                'state':'fail',
                                'msg':u'远程文件大于%sM,实际大小%2fM'%(MAX_UPLOAD_SIZE,file_size)
                            }})
                        continue
                    # if file exists on master,skip pull from minion.
                    file_info = FileInfo.objects.get(md5sum=md5sum)
                    full_path = REL_FILE_UPLAOD_FOLDER + file_info.path
                    # if not os.path.isfile(full_path):
                    if not fileserver_file_exists(file_info.md5sum):
                        logger.debug("## master saved file missing, fileinfo_id:%s,path:%s"%(file_info.pk,full_path))
                        RunningResult.objects.create(step=history_step,content=u"文件在fileserver上不存在,即将执行拉取步骤")
                        raise FileInfo.DoesNotExist
                    RunningResult.objects.create(step=history_step,content=u"文件在fileserver上已存在,跳过拉取步骤")
                    logger.debug("## remote source already on master, skip pull, info id:%s."%(file_info.pk))

                    logger.debug("## file size ok, size is %2fM"%file_size)
                    RunningResult.objects.create(step=history_step,content=u"文件大小:%2fM, 符合要求."%(file_size))

                    record = UploadRecord.objects.create(
                        user_name=user_name,
                        fileinfo=file_info,
                        file_name=os.path.basename(path),
                        src_ip=remote_ip,
                        location_type = enum_template.UPLOAD_TYPE_REMOTE,
                        remote_path = path,
                        remote_account = None
                    )
                    src_paths.add((record.pk,input_path))
                except FileInfo.DoesNotExist:
                    logger.debug("## remote source not on master, start pull remote file to syndic recursively...")
                    # pull remote file to syndic recursively
                    final_path = path
                    RunningResult.objects.create(step=history_step,content=u"开始文件拉取...",progress=start+1)
                    while True:
                        syndic_id = rc.hget(DETAIL_KEY_PREFIX+remote_minion_id,'master')
                        if syndic_id:
                            logger.debug("## start transfer file from %s to upper master: %s"%(remote_minion_id,syndic_id))
                            # res = client.cmd(remote_minion_id,'cp.push',[final_path]) # push file to upper master.
                            if syndic_id in local_ips:
                                arg = 'curl -F "upField=@{0}" -F "send_file_username={1}" -F "send_file_hash={2}" {3} -k'\
                                    .format(final_path,user_name,md5sum,MAPPED_FILE_SERVER_HOST)
                                logger.debug("curl args:{0}".format(arg))
                                RunningResult.objects.create(step=history_step,content=u"开始从%s拉取文件到文件服务器"%(remote_minion_id),progress=start+1)
                                status_ok,res = send_single_api_request(remote_minion_id,'cmd.run',[arg])
                                logger.debug("curl result:{0}".format(res))
                                if status_ok:
                                    curl_res = res[remote_minion_id]
                                    curl_info = curl_res[:curl_res.index("{\"")]
                                    curl_res = json.loads(curl_res[curl_res.index("{\""):])
                                    if curl_res['status']==200:
                                        r_record = UploadRecord.objects.get(pk=curl_res['result']['record_id'])
                                        r_record.remote_path = path
                                        r_record.src_ip = remote_ip
                                        r_record.save()
                                        src_paths.add((r_record.pk,input_path))
                                        print "file curled to fileserver,",res
                                        RunningResult.objects.create(step=history_step,content=u"文件已成功拉取到文件服务器.\n%s"%(curl_info))
                                    else:
                                        RunningResult.objects.create(step=history_step,content=u"文件服务器保存文件失败.\n%s"%(curl_info))
                                print res
                                ## already in top, break loop
                                break
                            else:
                                RunningResult.objects.create(step=history_step,content=u"开始从%s拉取到%s"%(remote_minion_id,syndic_id),progress=start+1)
                                push_count = 0
                                while push_count < 3:
                                    logger.debug("start api request cp.push, round: {0}".format(push_count))
                                    status_ok, res = send_single_api_request(remote_minion_id, 'cp.push', [final_path])
                                    if status_ok and res.get(remote_minion_id, ""):
                                        break
                                    push_count += 1
                            logger.debug("## push result:%s,path:%s"%(res,final_path))
                            state = res.get(remote_minion_id,"")
                            if state==True:
                                # pull file from syndic to master.
                                final_path = "/var/cache/salt/master/minions/%s/files/%s"%(remote_minion_id,final_path.strip("/"))
                                remote_minion_id = syndic_id
                            else:
                                fail_transfer_items.update({
                                    input_path:{
                                        'state':'fail',
                                        'msg': u"从 %s 拉取文件到 %s 失败!"%(remote_minion_id,syndic_id)
                                    }})
                                RunningResult.objects.create(step=history_step,content=u"从 %s 拉取文件到 %s 失败!"%(remote_minion_id,syndic_id))
                                raise Exception("pull file from %s to %s failed!"%(remote_minion_id,syndic_id))
                            RunningResult.objects.create(step=history_step,content=u"文件拉取成功,file:%s"%input_path)
                        else:
                            logger.debug("file already on top master, begin transferring downwards...")
                            break
                    logger.debug("## final path on master: %s"%final_path)

                item.record = record
                item.save()
                ## create remote HistoryFileInfo. replaced.
            except:
                fail_ids_set = set(online_agents)
                fail_transfer_items.update({
                    input_path:{
                        'state':'fail',
                        'msg':u"未知错误,从%s获取文件失败"%(remote_ip)
                    }})
                error = traceback.format_exc()
                logger.error(error)
                RunningResult.objects.create(step=history_step,content=u"从%s获取文件失败"%(remote_ip))
                RunningResult.objects.create(step=history_step,content=u"error :%s"%(error))
                pass
            RunningResult.objects.create(step=history_step,content=u"%s上的远程文件%s处理结束."%(remote_ip,input_path),progress=progress)
        logger.debug("src_paths:%s"%src_paths)
        logger.debug("========= end transfer remote files to master ==========")
        RunningResult.objects.create(step=history_step,content=u" 远程文件预处理结束  ",progress=35)
    # transfer file according to upload info.
    if local_file_records.count()>0:
        logger.debug("## start handle local file transfer:%s"%local_file_records.values_list('id'))
        RunningResult.objects.create(step=history_step,content=u" 开始本地文件预处理  ",progress=35)
        for item in local_file_records:
            try:
                record = item.record
                src_paths.add((record.pk,record.file_name))
                ## create local HistoryFileInfo. replaced.
            except:
                RunningResult.objects.create(step=history_step,content=u"获取文件记录失败,record id:%s"%(item.pk))
                logger.error("get record info fail!")
                error = traceback.format_exc()
                RunningResult.objects.create(step=history_step,content=u"ERROR :%s"%(error))
                logger.error(error)
                history_step.end_time = datetime.datetime.now()
                history_step.delta_time = (history_step.end_time - history_step.start_time).seconds
                history_step.result = enum_history.RESULT_FAIL
                history_step.save()

                return {
                    "status":500,
                    "result":{
                        "msg": u"未知错误!"
                    }
                }
        RunningResult.objects.create(step=history_step,content=u" 本地文件预处理结束  ",progress=40)

    start = progress = 40
    if src_paths:
        part = 50/len(src_paths)
        s_part = part/4
    for pk,ori_path in src_paths:

        RunningResult.objects.create(step=history_step,content=u" 开始批量分发文件:%s  "%(ori_path),progress=progress)
        try:
            record = UploadRecord.objects.get(id=pk)
            path = record.fileinfo.path
            file_name = record.file_name
            imd5sum = record.fileinfo.md5sum

            # transfer files to syndics if need.
            if syndics:
                tmp_syndics = set(syndics)
                syndic_path = "%s%s"%(SYNDIC_MASTER_FILE_CACHE,path)
                logger.debug("record_id:%s"%record.pk)
                # check if syndic already has the file.
                logger.debug("## start check syndic cache file, path:%s,md5:%s"%(syndic_path,imd5sum))
                # cache_check_result = client.cmd(list(syndics),'file.get_sum',[syndic_path,'md5'],expr_form="list") # get remote files's md5
                _,cache_check_result = send_single_api_request(list(syndics),'file.get_sum',[syndic_path,'md5'],expr_form="list")
                for key in syndics:
                    if cache_check_result.get(key,"") == imd5sum:
                        RunningResult.objects.create(step=history_step,content=u"文件在syndic上已存在")
                        logger.debug("## syndic cache %s already has the file,skip transfer."%key)
                        tmp_syndics.remove(key)
                if len(tmp_syndics)==0:
                    RunningResult.objects.create(step=history_step,content=u"所有syndic都已缓存该文件")
                    logger.debug("## no syndic need to recache the file, skip syndic transfer for file: %s"%path)
                else:
                    RunningResult.objects.create(step=history_step,content=u" 开始从文件服务器分发文件到syndic")
                    logger.debug("## file not found, start transter file [%s] to syndics:%s"%(ori_path,",".join(list(syndics))))
                    # logger.debug((list(tmp_syndics),"cp.get_ file",["salt://%s"%path,syndic_path]))
                    logger.debug("try remove syndic existing target path files...")
                    # sync_remove_result = client.cmd(list(tmp_syndics),"file.remove",[syndic_path],expr_form="list")
                    _,sync_remove_result = send_single_api_request(list(tmp_syndics),"file.remove",[syndic_path],expr_form="list")
                    logger.debug("sync_remove_result:%s"%sync_remove_result)
                    # sync_result = client.cmd(list(tmp_syndics),"cp.get_ file",["salt://%s"%path,syndic_path],kwarg={"makedirs":True,"gzip":3},expr_form="list")
                    # _,sync_result = send_single_api_request(list(tmp_syndics),"cp.get_file",["salt://%s"%path,syndic_path],kwarg={"makedirs":True,"gzip":3},expr_form="list")
                    _,sync_result = fileserver_get_file(list(tmp_syndics),imd5sum,syndic_path,expr_form="list")
                    print sync_result
                    # RunningResult.objects.create(step=history_step,content=u"syndic推送结果:%s"%(sync_result))
                    logger.debug("## result:%s"%sync_result)
                    has_fail = False
                    for key in tmp_syndics:
                        value = sync_result.get(key,"")
                        if not value or str(value).__contains__("MinionError"):
                            msg = u"分发文件%s到syndic节点%s失败"%(file_name,key)
                            logger.error(msg)
                            logger.debug(value)
                            RunningResult.objects.create(step=history_step,content=u"推送到%s失败\n%s"%(key,value),progress=start)
                            fail_transfer_items.update({
                                ori_path:{
                                    'state':'fail',
                                    'msg':msg
                                }})
                            has_fail = True
                            break
                    if has_fail:
                        fail_ids_set = set(online_agents)
                        RunningResult.objects.create(step=history_step,content=u"推送文件%s到%s失败"%(ori_path,syndics))
                        continue
                    start+=1
                    RunningResult.objects.create(step=history_step,content=u"推送文件到syndic结束",progress=start)
            progress+=s_part
            # transfer files to destination
            logger.debug("=== start send [%s] to final destinations.."%(path))
            RunningResult.objects.create(step=history_step,content=u"开始分发文件",progress=progress)
            failed_minions = list(online_agents)
            counter=3
            _success_minions = set()
            ss_part = s_part/counter
            while counter> 0 and failed_minions:
                _fail_minions = set()
                counter-=1
                progress+=ss_part
                RunningResult.objects.create(step=history_step,content=u"开始执行第%s次往%s分发文件%s"%(3-counter,failed_minions,ori_path),progress=progress)
                logger.debug("#================ trans to dst for the %s time,minions:%s ==========="%(3-counter,list(failed_minions)))
                # original_path = "%s/%s"%(target_path,file_name)
                # crypt_path = "%s/%s"%(target_path,str(time.time()))
                # logger.debug((path,original_path,crypt_path))
                target_pth = os.path.join(target_path,file_name)
                logger.debug("## try remove minion existing files...")
                # trans_remove_result = client.cmd(failed_minions,"file.remove",[target_pth],expr_form="list")
                _,trans_remove_result = send_single_api_request(failed_minions,"file.remove",[target_pth],expr_form="list")
                logger.debug("## remove existing files result:%s"%trans_remove_result)
                logger.debug(("command:",failed_minions,"cp.get_ file",["salt://%s"%path,"target:%s"%(target_pth)]))
                # trans_result = client.cmd(failed_minions,"cp.get_ file",["salt://%s"%path,target_pth],kwarg={"makedirs":True,"gzip":3},expr_form="list")
                status_ok,trans_result = send_single_api_request(failed_minions,"cp.get_file",["salt://%s"%path,target_pth],kwarg={"makedirs":True,"gzip":3},expr_form="list")
                logger.debug("## minion get_file result:%s"%trans_result)
                if not status_ok:
                    RunningResult.objects.create(step=history_step,content=u"文件传输失败, 返回结果: %s"%(trans_result))
                    continue
                RunningResult.objects.create(step=history_step,content=u"minion推送结果: %s"%(trans_result))
                for key in failed_minions:
                    if not trans_result.get(key,""):
                        RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"第%s次传输失败,file: %s"%(3-counter,ori_path),progress=start)
                        _fail_minions.add(key)
                    else:
                        RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"传输成功,file: %s"%(ori_path))
                    start+=1

                ### cp.get_file transfer ok minions
                success_ids = [suc_id for suc_id in failed_minions if suc_id not in _fail_minions]
                if len(success_ids)==0:
                    RunningResult.objects.create(step=history_step,content=u"本轮无成功传输的文件")
                    continue
                # rename_result = client.cmd(failed_minions,"file.rename",[crypt_path,original_path],expr_form="list")

                # logger.debug("rename path %s,rename minion result:%s"%((crypt_path,original_path),rename_result))
                # check_hash_result = client.cmd(success_ids,"file.get_hash",[target_pth,'md5'],expr_form="list")
                progress+=ss_part
                status_ok,check_hash_result = send_single_api_request(success_ids,"file.get_hash",[target_pth,'md5'],expr_form="list")
                RunningResult.objects.create(step=history_step,content=u"minion上%s的md5检查结果:%s"%(ori_path,check_hash_result),progress=progress)
                logger.debug("check_hash_result:%s"%check_hash_result)

                ### add md5 check fail item to list.
                for key in success_ids:
                    if check_hash_result.get(key,"") != imd5sum:
                        _fail_minions.add(key)
                        RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"第%s次分发HASH校验失败, file: %s, hash: %s"%(3-counter,ori_path,check_hash_result.get(key,"")),progress=start)
                    else:
                        RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"md5校验成功, path: %s, md5: %s"%(trans_result.get(key,ori_path),check_hash_result.get(key,"")))

                ### refresh success_ids.
                success_ids = [suc_id for suc_id in failed_minions if suc_id not in _fail_minions]

                progress+=ss_part
                ### ====== start renaming for chinese files if need ===============
                if target_pth!=target_pth.encode("GBK"):
                    non_utf8_agents =[]
                    for minion in success_ids:
                        locale = rc.hget(DETAIL_KEY_PREFIX+minion,"default_encoding")
                        if locale and str(locale).lower() not in ["utf-8","utf8"]:
                            non_utf8_agents.append(minion)
                    try:
                        logger.debug("non utf8 agents:%s"%(','.join(non_utf8_agents)))
                        if len(non_utf8_agents)>0:
                            RunningResult.objects.create(step=history_step,content=u"开始非utf8机器上的文件名编码转换:%s"%(','.join(non_utf8_agents)))
                            logger.debug("### start renaming filenames on agents:%s"%(','.join(non_utf8_agents)))
                            # client.cmd(failed_minions,"file.remove",[target_pth.encode("GBK")],expr_form="list")
                            # client.cmd(failed_minions,"file.rename",[target_pth,target_pth.encode("GBK")],expr_form="list")
                            #### handle remove result, if target file exists, rename will fail.
                            remove_status_ok,remove_result = send_single_api_request(non_utf8_agents,"file.remove",[target_pth.encode("GBK")],expr_form="list")
                            logger.debug("UTF-8 remove result:{0}".format(remove_result))
                            if not remove_status_ok or not remove_result or not isinstance(remove_result,dict):
                                for key in non_utf8_agents:
                                    RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"文件名编码转换失败,请修改为英文后重试")
                                raise Exception(u"执行结果返回错误或无响应")
                            for key in non_utf8_agents:
                                if remove_result.get(key,"") != True:
                                    _fail_minions.add(key)
                                    RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"文件名编码转换失败,请修改为英文后重试")

                            ##### handle rename result.
                            rename_status_ok,rename_result = send_single_api_request(non_utf8_agents,"file.rename",[target_pth,target_pth.encode("GBK")],expr_form="list")
                            logger.debug("UTF-8 rename result:{0}".format(rename_result))
                            if not rename_status_ok or not rename_result or not isinstance(rename_result,dict):
                                for key in non_utf8_agents:
                                    RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"文件名编码转换失败,请修改为英文后重试")
                                raise Exception(u"执行结果返回错误或无响应")
                            for key in non_utf8_agents:
                                if not rename_result.get(key,False):
                                    _fail_minions.add(key)
                                    RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"文件名编码转换失败,请修改为英文后重试")
                                else:
                                    RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"文件名编码转换成功.")
                            logger.debug("### renaming file end!")

                            RunningResult.objects.create(step=history_step,content=u"文件名编码转换ok.",progress=progress)
                        else:
                            logger.debug("### no agents has no-utf8 defaultdecoding, skip rename process.")
                    except Exception,e:
                        error = traceback.format_exc()
                        logger.error("renaming error!")
                        logger.error(error)
                        RunningResult.objects.create(step=history_step,content=u"文件名编码转换失败:%s"%(e.message),progress=progress)
                        _fail_minions = _fail_minions.union(set(non_utf8_agents))
                        [success_ids.remove(item) for item in _fail_minions]

                ### total success minions this time for file xxx.
                _success_minions = _success_minions.union(success_ids)

                ### next total minions to run.
                failed_minions = list(set(online_agents).difference(_success_minions))

            ## total trans fail minion for file $file
            trans_fail_minions = online_agents.difference(_success_minions)

            # logger.debug("final fail trans minions for file [%s]:%s"%(ori_path,list(trans_fail_minions)))
            for key in trans_fail_minions:
                ip = minion_id_map.get(key)
                RunningResult.objects.create(step=history_step,ip=ip,content=u"文件分发失败: %s"%(ori_path),progress=start)
                fail_ids_set.add(key)
                minion_result.setdefault(ip,{}).update({ori_path: {
                    "state": 'fail',
                    "msg": u"分发失败"
                }})
                start+=1
        except Exception,e:
            fail_ids_set = set(online_agents)
            error = traceback.format_exc()
            RunningResult.objects.create(step=history_step,content=u"处理文件出错,分发失败:%s"%(ori_path))
            RunningResult.objects.create(step=history_step,content=error)
            logger.error("## error handling path:%s,record_id:%s"%(ori_path, pk))
            logger.error(error)
            fail_transfer_items.update({
                ori_path:{
                    'state':'fail',
                    'msg': u'分发失败!'
                }})
        RunningResult.objects.create(step=history_step,content=u" 该文件分发处理结束:%s  "%(ori_path))

    logger.error("## Fail files:%s"%fail_transfer_items)

    step_msg = u'步骤执行成功'
    if len(fail_transfer_items.keys())>0 or len(fail_ids_set)>0 or offline_agents_num>0:
        step_msg = u'步骤执行失败'
        history_step.result = enum_history.RESULT_FAIL
        history_step.fail_ips = json.dumps([minion_id_map.get(key) for key in fail_ids_set])
        # history.status = enum_history.STATUS_FAIL
        status = 500
    else:
        history_step.result = enum_history.RESULT_SUCCESS
        # history.status = enum_history.STATUS_SUCCESS

    history_step.success_ips = json.dumps([minion_id_map.get(key) for key in online_agents.difference(fail_ids_set)])

    history_step.end_time = datetime.datetime.now()
    history_step.delta_time = (history_step.end_time - history_step.start_time).seconds
    history_step.save()

    RunningResult.objects.create(step=history_step, content=u"所有文件分发执行结束,%s"%(step_msg),progress=100)

    logger.debug("minion_result:%s"%minion_result)
    return {
        "status":status
    }

def handle_step_pull_file(history_step):
    '''
         处理从minion上的文件拉取
         所有待拉取的文件都在minion上, 不存在混合类型的情况.
         文件目标位置是另一台minion, syndic不会进行业务处理.
    '''

    status = 200
    history_step.start_time = datetime.datetime.now()
    history_step.result = enum_history.RESULT_PROCESSING #正在执行中
    history_step.save()

    history = history_step.history
    user_name = history.user.username
    history_step_pull_file = _history.get_historyStepPullFile_by_params(step=history_step)
    if not history_step_pull_file:
        logger.error(" no pull file info found for history_step, his_id:{0}".format(history_step.id))
        return {
            "status":500,
            "result":{
                "msg": u"获取文件拉取列表失败"
            }
        }


    target_path = os.path.normpath(str(history_step_pull_file.pull_to)).replace("\\","/")
    file_paths = json.loads(history_step_pull_file.file_paths)

    src_paths = set()

    # final return result.
    minion_result = {}

    # 等待拉取的minion集合.
    ip_set = set(json.loads(history.target) if history.target else [])
    if history_step.is_setting:
        ip_set = set(json.loads(history_step.target) if history_step.target and eval(history_step.target) else ip_set)

    history_step.total_ips = json.dumps(list(ip_set))
    history_step.save()
    local_ips = get_master_addrs()

    # dict for minion-ip mapping.
    minion_id_map = {}

    # failed path-state map
    fail_transfer_items = {}

    # all failed ips
    fail_ids_set = set()

    # store minion belong to which syndic., {'syndic-B':set('minion-a','minon-b')}
    syndic_minion_map = {}

    RunningResult.objects.create(step=history_step,content=u"开始检查待拉取目标机器",progress=3)

    # Get syndic-id of the pull-to minion
    target_path_syndic = ""
    logger.debug("Pull File ##  start get syndic of target minion  ...")
    minion_id = rc.get(IP_KEY_PREFIX + history_step_pull_file.pull_to_ip)
    if minion_id and rc.hexists(DETAIL_KEY_PREFIX + minion_id, 'master'):
        syndic = rc.hget(DETAIL_KEY_PREFIX + minion_id, 'master')
        if not syndic or syndic in local_ips:
            return {
                "status": 500,
                "result": {
                    "msg": u"拉取目标机器只能为minion"
                }
            }
        target_path_syndic = syndic
    logger.debug("Pull File ##  syndic of target [{0}] is [{1}]".format(history_step_pull_file.pull_to_ip,target_path_syndic))

    logger.debug("Pull File ##  start check duplicate ips  ...")
    dup_ips = set()
    for ip in ip_set:
        minion_id = rc.get(IP_KEY_PREFIX+ip)
        # 排除重复IP, 或多网卡IP
        if minion_id in minion_id_map.keys():
            RunningResult.objects.create(step=history_step,ip=ip,content=u"目标机器IP%s与本IP属同一台机器,跳过处理."%(ip),progress=5)
            logger.warning("IP %s has dup in minion ip_set:%s"%(ip,minion_id_map.get(minion_id)))
            dup_ips.add(ip)
            continue
        minion_id_map.update({minion_id:ip})
        # syndic_minion_map.setdefault(rc.hget(DETAIL_KEY_PREFIX + minion_id, 'master'),set()).add(minion_id)
        syndic_minion_map[minion_id] = rc.hget(DETAIL_KEY_PREFIX + minion_id, 'master')

    # Final target minions to pull files from
    ip_set = ip_set.difference(dup_ips)
    logger.debug("Pull File ##  Final target ip:%s"%ip_set)

    if len(ip_set)==0:
        history_step.end_time = datetime.datetime.now()
        history_step.delta_time = (history_step.end_time - history_step.start_time).seconds
        history_step.result = enum_history.RESULT_FAIL
        history_step.save()

        RunningResult.objects.create(step=history_step,content=u"可操作目标机器不能为空",progress=100)
        return {
            "status":500,
            "result":{
                "msg": u"可操作目标机器不能为空"
            }
        }
    RunningResult.objects.create(step=history_step,content=u"目标机器检查完成",progress=8)
    # logger.debug("Pull File ##  end check, syndics:%s,invalid_ips:%s"%(syndics,fail_ids_set))

    # get current input agent stasus.
    logger.debug("Pull File ##  start check online agent status")
    RunningResult.objects.create(step=history_step,content=u"开始获取目标机器当前agent状态",progress=9)
    id_list = list(set([rc.get(IP_KEY_PREFIX+ip) for ip in ip_set]))

    #### get online status from cache.
    cached_up_agents = rc.smembers(MINIONS_UP_SET_KEY)
    online_agents = set(cached_up_agents).intersection(set(id_list))
    online_agents_num = len(online_agents)
    offline_agents_num = len(id_list)-online_agents_num
    offline_agents = set(id_list).difference(online_agents)
    logger.debug("Pull File ##  online:%s,offline:%s"%(list(online_agents),list(offline_agents)))
    logger.debug("Pull File ##  check finished, online_num:%s,offline_num:%s.details,"%(online_agents_num,offline_agents_num))
    RunningResult.objects.create(step=history_step,content=u"检查结果,在线:%s,离线:%s"%
                                                           ([minion_id_map.get(id) for id in online_agents],
                                                            [minion_id_map.get(id) for id in offline_agents]),progress=12)

    target_minion_id = rc.get(IP_KEY_PREFIX+ history_step_pull_file.pull_to_ip)
    if target_minion_id not in set(cached_up_agents):
        msg = u"拉取到的目标机器当前离线, 终止拉取"
        RunningResult.objects.create(step=history_step,content=msg,progress=100)
        return {
            "status":500,
            "result":{
                "msg": msg
            }
        }

    history_step.total_ips = json.dumps([minion_id_map.get(id) for id in list(id_list)])
    history_step.abnormal_ips = json.dumps([minion_id_map.get(id) for id in list(offline_agents)])
    history_step.save()
    RunningResult.objects.create(step=history_step,content=u"获取所有agent状态结束",progress=13)
    for offline_agent in offline_agents:
        RunningResult.objects.create(ip=minion_id_map.get(offline_agent),step=history_step,content=u"拉取时agent离线,该机器执行拉取失败",progress=14)

    fail_ids_set = set()
    file_paths_length = len(file_paths)

    logger.debug("Pull File ##  start transfer remote src files to fileserver ==========")
    RunningResult.objects.create(step=history_step,content=u"开始处理所有待拉取文件",progress=15)

    remote_minion_ids = [rc.get(IP_KEY_PREFIX+remote_ip) for remote_ip in ip_set]

    # 存储远程文件hash, {'minion-id':{'file_path': 'md5'}}
    file_hash_dict = {}

    # files not exist in fileserver and wait to pull. format: {'file_path':['minion-a','minion-b']}
    files_source_to_pull_dict = {}
    start = 15
    for item in file_paths:
        # part = int(20/file_paths_length)
        path = item
        input_path = path
        path = os.path.normpath(path.replace('\\','/'))
        # remote_account_id = item.push_account

        try:

            logger.debug("Pull File ##  start handle remote source path:%s"%(path))
            RunningResult.objects.create(step=history_step,content=u"开始处理%s上的远程文件:%s"%(",".join(remote_minion_ids),input_path),progress=start)
            start += 1

            try:
                # check if remote file exists.
                logger.debug("Pull File ##  start handle remote file: %s"%path)

                status_ok,check_cmd=send_single_api_request(remote_minion_ids,'file.get_sum',[path,'md5'],expr_form="list")
                if status_ok:
                    for key in remote_minion_ids:
                        md5sum = str(check_cmd.get(key,""))
                        source_ip = minion_id_map.get(key)
                        if md5sum.find("File not found") > -1:
                            fail_ids_set.add(key)
                            RunningResult.objects.create(ip=source_ip,step=history_step,content=u"ERROR: 远程文件不存在,%s"%(input_path))
                            logger.warning("Pull File ##  remote source file not found:%s"%path)
                            continue
                        logger.debug("Pull File ##  md5 of remote source file:%s"%(md5sum))
                        file_hash_dict.setdefault(key,{}).setdefault(path,md5sum)
                        if fileserver_file_exists(md5sum):
                            RunningResult.objects.create(ip=source_ip,step=history_step,content=u"文件%s在fileserver上已存在, 跳过该文件获取, md5:%s"%(input_path,md5sum), progress=start)
                        else:
                            RunningResult.objects.create(ip=source_ip,step=history_step,content=u"文件%s在fileserver上不存在, 加入拉取列表"%(input_path),progress=start)
                            files_source_to_pull_dict.setdefault(input_path,list()).append(key)
                else:
                    msg = u"ERROR: API调用失败, 返回信息:\n%s"%(check_cmd)
                    logger.error(msg)
                    return {
                        "status": 500,
                        "result": {
                            "msg": msg
                        }
                    }
            except:
                error =  traceback.format_exc()
                logger.error(error)
                print error
            start += 1
        except:
            error =  traceback.format_exc()
            logger.error(error)
            print error

    start = 30
    # 在syndic上待推送到fileserver的文件列表
    success_push_files = {}
    for pull_path,pull_source_list in files_source_to_pull_dict.iteritems():

        logger.debug("Pull File ## start to pull file {0} from {1}".format(pull_path,",".join(pull_source_list)))
        RunningResult.objects.create(step=history_step,content=u"开始获取文件{1}, 目标机器:{0}".format(",".join(pull_source_list),pull_path),progress=start)

        logger.debug("Pull File ##  remote source not on master, start pull remote file to fileserver ...")
        final_path = pull_path

        pull_list = list(pull_source_list)
        retry = 1
        while retry < 4 and len(pull_list) > 0:
            start+=1
            status_ok, push_result = send_single_api_request(pull_list, 'cp.push', [final_path], expr_form='list')
            logger.debug("push_result: {0}".format(push_result))
            if status_ok:
                for key in pull_source_list:
                    push_res = push_result.get(key, "")
                    if push_res:
                        pull_list.remove(key)
                RunningResult.objects.create(step=history_step,content=u"文件获取成功, 返回: {0}".format(push_result),progress=start)
            else:
                msg = u"第{0}次执行拉取{1}失败, 原因:{2}".format(retry, pull_path, push_result)
                RunningResult.objects.create(step=history_step,content=msg,progress=start)
                logger.error("Pull File ## cp.push fail!!!!")
                logger.error(push_result)
            retry += 1

        [success_push_files.setdefault(pull_path,set()).add(item) for item in pull_source_list ]

    start = 40
    # 推送文件到fileserver.
    for pull_path,hosts in success_push_files.iteritems():
        for host in hosts:
            start += 1
            ip = minion_id_map.get(host)
            push_syndic = syndic_minion_map.get(host)
            final_path = "/var/cache/salt/master/minions/%s/files/%s"%(host,pull_path.strip("/"))
            md5sum = file_hash_dict.get(host,{}).get(pull_path,"")
            if not md5sum:
                logger.error("Pull File ## original file hash not found! skip handle")
                RunningResult.objects.create(ip= ip,step=history_step,content=u"原始文件hash获取失败, 跳过处理")
                continue
            arg = 'curl -F "upField=@{0}" -F "send_file_username={1}" -F "send_file_hash={2}" {3} -k'\
                                .format(final_path,user_name,md5sum,MAPPED_FILE_SERVER_HOST)
            logger.debug("Pull File ## curl args:{0}".format(arg))
            RunningResult.objects.create(step=history_step,content=u"开始从{0}拉取文件{1}到文件服务器".format(push_syndic,pull_path),progress=start)
            status_ok,res = send_single_api_request(push_syndic,'cmd.run',[arg])
            logger.debug("Pull File ## curl result:{0}".format(res))
            if status_ok:
                curl_res = res[push_syndic]
                curl_info = curl_res[:curl_res.index("{\"")]
                curl_res = json.loads(curl_res[curl_res.index("{\""):])
                if curl_res['status']==200:
                    r_record = UploadRecord.objects.get(pk=curl_res['result']['record_id'])
                    r_record.remote_path = pull_path
                    r_record.src_ip = ip
                    r_record.save()
                    src_paths.add((r_record.pk,pull_path))
                    print "file curled to fileserver,",res
                    start += 1
                    RunningResult.objects.create(ip= ip,step=history_step,content=u"文件已成功拉取到文件服务器.\n%s"%(curl_info),progress=start)
                    HistoryFileInfo.objects.create(
                        step=history_step,
                        remote_ip = ip,
                        push_account = None,
                        location_type = enum_template.UPLOAD_TYPE_REMOTE,
                        remote_path = pull_path,
                        record = r_record
                   )
                else:
                    RunningResult.objects.create(ip= ip,step=history_step,content=u"文件服务器保存文件失败.\n%s"%(curl_info))
            else:
                logger.error("Pull File ## api call error.!!!!")
                RunningResult.objects.create(ip= ip,step=history_step,content=u"保存文件到服务器失败. path:%s"%(pull_path))
                fail_ids_set.add(host)
            print res

    # 分发文件到minion上
    start = 50
    for minion_id, files in file_hash_dict.iteritems():
        syndic = syndic_minion_map.get(minion_id)
        ip = minion_id_map.get(minion_id)
        for file_path,md5sum in files.iteritems():
            file_name = os.path.basename(file_path)
            RunningResult.objects.create(step=history_step,content=u"开始拉取文件到目标位置, 文件: %s, 位置: %s.  "%(file_path,target_path),progress=start)
            start+=1
            file_info = FileInfo.objects.get(md5sum=md5sum)
            path = file_info.path
            syndic_path = "%s%s"%(SYNDIC_MASTER_FILE_CACHE, path)
            status_ok, cache_check_result = send_single_api_request(syndic,'file.get_sum',[syndic_path,'md5'])
            if not status_ok:
                RunningResult.objects.create(ip=ip, step=history_step,content=u"文件拉取失败, 路径: %s"%(file_path),progress=start)
                start+=1
                fail_ids_set.add(minion_id)
                continue
            if cache_check_result.get(syndic,"") == md5sum:
                RunningResult.objects.create(ip=ip, step=history_step,content=u"文件在syndic上已存在",progress=start)
                start+=1
            else:
                RunningResult.objects.create(ip=ip, step=history_step,content=u"文件未缓存, 开始执行拉取")
                _,sync_remove_result = send_single_api_request(syndic,"file.remove",[syndic_path])
                logger.debug("Pull File ## sync_remove_result:%s"%sync_remove_result)
                _,sync_result = fileserver_get_file(syndic,md5sum,syndic_path,expr_form="list")
                logger.debug("Pull File ## sync_get_url_result:%s"%sync_result)
                value = sync_result.get(syndic,"")
                if not value or str(value).__contains__("MinionError"):
                    RunningResult.objects.create(step=history_step,content=u"推送到%s失败\n%s"%(syndic,value),progress=start)
                    msg = u"分发文件%s到syndic节点%s失败"%(file_path,syndic)
                    logger.error(msg)
                    fail_ids_set.add(minion_id)
                else:
                    RunningResult.objects.create(step=history_step,content=u"推送到%s成功\n%s"%(syndic,value),progress=start)
                    start+=1

            RunningResult.objects.create(step=history_step,content=u"开始分发文件",progress=start)
            start+=1
            failed_minions = [target_minion_id]
            counter=3
            _success_minions = set()
            while counter> 0 and failed_minions:
                _fail_minions = set()
                counter-=1
                RunningResult.objects.create(ip=ip, step=history_step,content=u"第%s次往%s分发文件%s"%(3-counter,ip,file_path),progress=start)
                start+=1
                logger.debug("Pull File ## ================ trans to dst for the %s time,minions:%s ==========="%(3-counter,list(failed_minions)))
                target_pth = os.path.join(target_path,file_name).replace("[TARGET_IP]",history_step_pull_file.pull_to_ip)
                logger.debug("Pull File ## try remove minion existing files...")
                _,trans_remove_result = send_single_api_request(failed_minions,"file.remove",[target_pth],expr_form="list")
                logger.debug("Pull File ## remove existing files result:%s"%trans_remove_result)
                status_ok,trans_result = send_single_api_request(failed_minions,"cp.get_file",["salt://%s"%path,target_pth],kwarg={"makedirs":True,"gzip":3},expr_form="list")
                logger.debug("Pull File ## minion get_file result:%s"%trans_result)

                if not status_ok:
                    RunningResult.objects.create(ip=ip,step=history_step,content=u"文件传输失败, 返回结果: %s"%(trans_result))
                    continue
                RunningResult.objects.create(ip=ip,step=history_step,content=u"minion推送结果: %s"%(trans_result))
                for key in failed_minions:
                    if not trans_result.get(key,""):
                        RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"第%s次传输失败,file: %s"%(3-counter,file_path),progress=start)
                        _fail_minions.add(key)
                        continue
                    else:
                        RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"传输成功,file: %s"%(file_path))
                    start+=1

                ### cp.get_file transfer ok minions
                success_ids = [suc_id for suc_id in failed_minions if suc_id not in _fail_minions]
                if len(success_ids)==0:
                    RunningResult.objects.create(step=history_step,content=u"本轮无成功传输的文件")
                    continue
                status_ok,check_hash_result = send_single_api_request(success_ids,"file.get_hash",[target_pth,'md5'],expr_form="list")
                RunningResult.objects.create(step=history_step,content=u"minion上%s的md5检查结果:%s"%(target_pth,check_hash_result),progress=start)
                start+=1
                logger.debug("Pull File ## check_hash_result:%s"%check_hash_result)

                ### add md5 check fail item to list.
                for key in success_ids:
                    if check_hash_result.get(key,"") != md5sum:
                        _fail_minions.add(key)
                        RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"第%s次拉取hash校验失败, file: %s, hash: %s"%(3-counter,target_pth,check_hash_result.get(key,"")),progress=start)
                    else:
                        RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"md5校验成功, path: %s, md5: %s"%(trans_result.get(key,target_pth),check_hash_result.get(key,"")))

                ### refresh success_ids.
                success_ids = [suc_id for suc_id in failed_minions if suc_id not in _fail_minions]
                start+=1
                ### ====== start renaming for chinese files if need ===============
                if target_pth!=target_pth.encode("GBK"):
                    non_utf8_agents =[]
                    for minion in success_ids:
                        locale = rc.hget(DETAIL_KEY_PREFIX+minion,"default_encoding")
                        if locale and str(locale).lower() not in ["utf-8","utf8"]:
                            non_utf8_agents.append(minion)
                    try:
                        logger.debug("Pull File ## non utf8 agents:%s"%(','.join(non_utf8_agents)))
                        if len(non_utf8_agents)>0:
                            RunningResult.objects.create(step=history_step,content=u"开始非utf8机器上的文件名编码转换:%s"%(','.join(non_utf8_agents)))
                            logger.debug("Pull File ## start renaming filenames on agents:%s"%(','.join(non_utf8_agents)))
                            remove_status_ok,remove_result = send_single_api_request(non_utf8_agents,"file.remove",[target_pth.encode("GBK")],expr_form="list")
                            logger.debug("Pull File ## UTF-8 remove result:{0}".format(remove_result))
                            if not remove_status_ok or not remove_result or not isinstance(remove_result,dict):
                                for key in non_utf8_agents:
                                    RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"文件名编码转换失败,请修改为英文后重试")
                                raise Exception(u"执行结果返回错误或无响应")
                            for key in non_utf8_agents:
                                if remove_result.get(key,"") != True:
                                    _fail_minions.add(key)
                                    RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"文件名编码转换失败,请修改为英文后重试")

                            ##### handle rename result.
                            rename_status_ok,rename_result = send_single_api_request(non_utf8_agents,"file.rename",[target_pth,target_pth.encode("GBK")],expr_form="list")
                            logger.debug("Pull File ## UTF-8 rename result:{0}".format(rename_result))
                            if not rename_status_ok or not rename_result or not isinstance(rename_result,dict):
                                for key in non_utf8_agents:
                                    RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"文件名编码转换失败,请修改为英文后重试")
                                raise Exception(u"执行结果返回错误或无响应")
                            for key in non_utf8_agents:
                                if not rename_result.get(key,False):
                                    _fail_minions.add(key)
                                    RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"若文件名编码转换失败,请修改为英文后重试")
                                else:
                                    RunningResult.objects.create(step=history_step,ip=minion_id_map.get(key),content=u"文件名编码转换成功.")
                            logger.debug("Pull File ## renaming file end!")

                            RunningResult.objects.create(step=history_step,content=u"文件名编码转换ok.",progress=start)
                        else:
                            logger.debug("Pull File ## no agents has no-utf8 defaultdecoding, skip rename process.")
                    except Exception,e:
                        error = traceback.format_exc()
                        logger.error("Pull File ## renaming error!")
                        logger.error(error)
                        RunningResult.objects.create(step=history_step,content=u"文件名编码转换失败:%s"%(e.message),progress=start)
                        _fail_minions = _fail_minions.union(set(non_utf8_agents))
                        [success_ids.remove(item) for item in _fail_minions]

                ### total success minions this time for file xxx.
                _success_minions = _success_minions.union(success_ids)

                ### next total minions to run.
                failed_minions = list(set([target_minion_id]).difference(_success_minions))

            ## total trans fail minion for file $file
            trans_fail_minions = set([target_minion_id]).difference(_success_minions)

            logger.debug("final fail trans minions for file [%s]:%s"%(file_path,list(trans_fail_minions)))
            start+=1
            for key in trans_fail_minions:
                ip = minion_id_map.get(key)
                RunningResult.objects.create(step=history_step,ip=ip,content=u"文件拉取失败: %s"%(file_path),progress=start)
                fail_ids_set.add(key)
            RunningResult.objects.create(ip=ip, step=history_step,content=u"文件拉取成功, 文件类型: %s"%(file_path),progress=start)


    step_msg = u'步骤执行成功'
    if len(fail_transfer_items.keys())>0 or len(fail_ids_set)>0 or offline_agents_num>0:
        step_msg = u'步骤执行失败'
        history_step.result = enum_history.RESULT_FAIL
        history_step.fail_ips = json.dumps([minion_id_map.get(key) for key in fail_ids_set])
        status = 500
    else:
        history_step.result = enum_history.RESULT_SUCCESS

    history_step.success_ips = json.dumps([minion_id_map.get(key) for key in online_agents.difference(fail_ids_set)])
    history_step.end_time = datetime.datetime.now()
    history_step.delta_time = (history_step.end_time - history_step.start_time).seconds
    history_step.save()

    RunningResult.objects.create(step=history_step, content=u"所有文件分发执行结束,%s"%(step_msg),progress=100)

    logger.debug("Pull File ## minion_result:%s"%minion_result)
    return {
        "status":status
    }

def handle_step_text(history_step):
    '''
         文本步骤处理, 无特殊操作.
    '''
    status = 200
    history_step.start_time = datetime.datetime.now()
    history_step.result = enum_history.RESULT_PROCESSING #正在执行中
    history_step.save()

    history_step_text = _history.get_historyStepText_by_params(step=history_step)
    if not history_step_text:
        logger.error("no history step text found for history_step, his_id:{0}".format(history_step.id))
        return {
            "status":500,
            "result":{
                "msg": u"文本步骤执行失败"
            }
        }

    history_step.result = enum_history.RESULT_SUCCESS
    history_step.end_time = datetime.datetime.now()
    history_step.delta_time = (history_step.end_time - history_step.start_time).seconds
    history_step.save()

    return {
        "status":status
    }

def pre_handle_job(job,user):
    '''
        start job now.
    '''

    status = 500
    data = {}
    history = _history.create_history_by_params(job=job,name=job.name)
    msg = ""
    try:
        history.remarks = job.remarks
        history.mode = job.mode
        history.account = job.account
        history.target = job.target
        history.start_time = datetime.datetime.now()
        history.user = user
        history.status = enum_history.STATUS_PROCESSING
        history.save()

        job_steps = _job.get_jobSteps_by_params(job=job,is_checked=True,is_delete=False).order_by('order')
        for job_step in job_steps:
            history_step = _history.get_or_create_historyStep_by_params(history=history,jobstep=job_step)[0]
            history_step.name = job_step.name
            history_step.describe = job_step.describe
            history_step.order = job_step.order
            history_step.target = job_step.target
            history_step.is_setting = job_step.is_setting
            history_step.account = job_step.account
            history_step.result = enum_history.RESULT_NOT_START
            history_step.total_ips = json.dumps(json.loads(job_step.target) if job_step.target else [] or json.loads(job.target) if job.target else [])
            
            history_step.save()
            try:
                if job_step.step_type == enum_template.STEP_TYPE_PULL_FILE:
                    # create history job pull file info.
                    job_step_pull_file = JobStepPullFile.objects.get(step=job_step)

                    history_step_pull_file = _history.get_or_create_historyStepPullFile_by_params(
                        step=history_step,
                        limit=job_step_pull_file.limit,
                        pull_to=job_step_pull_file.pull_to,
                        pull_to_ip=job_step_pull_file.pull_to_ip,
                        file_paths=job_step_pull_file.file_paths
                    )[0]
                    history_step_pull_file.save()

                elif job_step.step_type == enum_template.STEP_TYPE_PUSH_FILE:

                    # create history job file info.
                    job_file_records = JobFileInfo.objects.filter(step=job_step)
                    remote_file_records = job_file_records.filter(location_type=enum_template.UPLOAD_TYPE_REMOTE)
                    local_file_records = job_file_records.filter(location_type=enum_template.UPLOAD_TYPE_LOCAL)

                    for item in remote_file_records:
                        path = item.remote_path
                        remote_ip = str(item.remote_ip)
                        path = os.path.normpath(path.replace('\\','/'))
                        HistoryFileInfo.objects.create(
                            step=history_step,
                            remote_ip = remote_ip,
                            push_account = None,
                            location_type = enum_template.UPLOAD_TYPE_REMOTE,
                            remote_path = path,
                        )

                    for item in local_file_records:
                        record = item.record
                        HistoryFileInfo.objects.create(
                            step=history_step,
                            remote_ip = record.src_ip,
                            push_account = None,
                            location_type = enum_template.UPLOAD_TYPE_LOCAL,
                            remote_path = record.file_name,
                            record = record
                        )

                    # create history step push file record.
                    job_step_push_file = JobStepPushFile.objects.get(step=job_step)
                    history_step_push_file = _history.get_or_create_historyStepPushFile_by_params(
                        step=history_step,
                        limit=job_step_push_file.limit,
                        push_to=job_step_push_file.push_to,
                    )[0]
                    history_step_push_file.save()

                elif job_step.step_type == enum_template.STEP_TYPE_SCRIPT:
                    jobStepScript = _job.get_jobStepScript_by_params(step=job_step)
                    historyStepScript = _history.create_historyStepScript_by_params(step=history_step,version=jobStepScript.version)
                    historyStepScript.parameter = jobStepScript.parameter
                    historyStepScript.timeout = jobStepScript.timeout
                    historyStepScript.save()

                elif job_step.step_type == enum_template.STEP_TYPE_TEXT:
                    job_step_text = _job.get_jobStepText_by_params(step=job_step)
                    history_step_text = _history.get_or_create_historyStepText_by_params(
                        step=history_step
                    )[0]
                    history_step_text.describe = job_step_text.describe
                    history_step_text.save()
            except Exception,e:
                error = traceback.format_exc()
                logger.error(error)
                history_step.result = enum_history.RESULT_FAIL
                history_step.save()
                msg = u"作业步骤【{1}】预处理失败".format(history_step.order,history_step.name)
                RunningResult.objects.create(step=history_step,content=u"步骤【{1}】处理失败,原因如下: \n{0}".format(error,history_step.name),progress=100)
                raise
        status=200
    except:
        error = traceback.format_exc()
        logger.error(error)
        data['msg'] = u'执行作业出错' if not msg else msg
        history.status = enum_history.STATUS_FAIL
        history.end_time = datetime.datetime.now()
        history.delta_time = (history.end_time - history.start_time).seconds
        history.save()
    data['history_id'] = history.id
    return {
        "status": status,
        "result": data
    }

def _handle_job_auto(history,history_job_steps):
    status = enum_history.STATUS_SUCCESS
    result = {}

    for history_step in history_job_steps:
        step_type = history_step.jobstep.step_type
        try:
            if step_type == enum_template.STEP_TYPE_PULL_FILE:
                result = handle_step_pull_file(history_step)
            elif step_type == enum_template.STEP_TYPE_PUSH_FILE:
                result = handle_step_push_file(history_step)
            elif step_type == enum_template.STEP_TYPE_TEXT:
                result = handle_step_text(history_step)
            elif step_type == enum_template.STEP_TYPE_SCRIPT:
                result = handle_step_script(history_step)
            if not result or result['status'] != 200:
                status = enum_history.STATUS_FAIL
                break
        except:
            error = traceback.format_exc()
            logger.error(error)
            print error
            status = enum_history.STATUS_FAIL
            break
        
    history.end_time = datetime.datetime.now()
    history.status = status
    history.delta_time = (history.end_time - history.start_time).seconds
    history.save()
    msg = "### handle job done, current threading name: {0}, history id: {1}".format(threading.currentThread().getName(),history.id)
    logger.debug(msg)

def _handle_job_mannual(history,history_step):
    status = enum_history.STATUS_SUCCESS
    result = {}
    history_job_steps = _history.get_historySteps_by_params(history=history).order_by('-order')
    step_type = history_step.jobstep.step_type
    try:
        if step_type == enum_template.STEP_TYPE_PULL_FILE:
            result = handle_step_pull_file(history_step)
        elif step_type == enum_template.STEP_TYPE_PUSH_FILE:
            result = handle_step_push_file(history_step)
        elif step_type == enum_template.STEP_TYPE_TEXT:
            result = handle_step_text(history_step)
        elif step_type == enum_template.STEP_TYPE_SCRIPT:
            result = handle_step_script(history_step)
        if not result or result['status'] != 200:
            status = enum_history.STATUS_FAIL
    except:
        error = traceback.format_exc()
        print error
        status = enum_history.STATUS_FAIL
    
    if history_step == history_job_steps[0]:
        history.end_time = datetime.datetime.now()
        history.status = status
        history.delta_time = (history.end_time - history.start_time).seconds
        history.save()
    else:
        if status == enum_history.STATUS_SUCCESS:
            index = list(history_job_steps).index(history_step)
            history_step_next = history_job_steps[index-1]
            history_step_next.result = enum_history.RESULT_WAIT_USER
            history_step_next.save()
            
#def _handle_job_mix(history,history_job_steps):
#    status = enum_history.STATUS_SUCCESS
#    result = {}
#    length = len(history_job_steps)
#    index = 0
#    for history_step in history_job_steps:
#        index += 1
#        step_type = history_step.jobstep.step_type
#        if step_type == enum_template.STEP_TYPE_PULL_FILE:
#            result = handle_step_pull_file(history_step)
#        elif step_type == enum_template.STEP_TYPE_PUSH_FILE:
#            result = handle_step_push_file(history_step)
#        elif step_type == enum_template.STEP_TYPE_TEXT:
#            result = handle_step_text(history_step)
#            if index < length:
#                history_step_next = history_job_steps[index]
#                history_step_next.result = enum_history.RESULT_WAIT_USER
#                history_step_next.save()
#            break
#        elif step_type == enum_template.STEP_TYPE_SCRIPT:
#            result = handle_step_script(history_step)
#        if not result or result['status'] != 200:
#            status = enum_history.STATUS_FAIL
#            break
#        
#    if index == length:
#        history.end_time = datetime.datetime.now()
#        history.status = status
#        history.delta_time = (history.end_time - history.start_time).seconds
#        history.save()
        
def _handle_job_mix(history,history_job_steps):
    status = enum_history.STATUS_SUCCESS
    result = {}
    length = len(history_job_steps)
    index = 0
    for history_step in history_job_steps:
        index += 1
        step_type = history_step.jobstep.step_type
        if step_type == enum_template.STEP_TYPE_PULL_FILE:
            result = handle_step_pull_file(history_step)
        elif step_type == enum_template.STEP_TYPE_PUSH_FILE:
            result = handle_step_push_file(history_step)
        elif step_type == enum_template.STEP_TYPE_TEXT:
            result = handle_step_text(history_step)
        elif step_type == enum_template.STEP_TYPE_SCRIPT:
            result = handle_step_script(history_step)
        
        if not result or result['status'] != 200:
            status = enum_history.STATUS_FAIL
            break
        elif index < length:
            history_step_next = history_job_steps[index]
            step_type_next = history_step_next.jobstep.step_type
            if step_type_next == enum_template.STEP_TYPE_TEXT:
                history_step_next.result = enum_history.RESULT_WAIT_USER
                history_step_next.save()
                break
        
    if index == length:
        history.end_time = datetime.datetime.now()
        history.status = status
        history.delta_time = (history.end_time - history.start_time).seconds
        history.save()

def _handle_job(history_id,history_step_id=0,operation=''):
    history = _history.get_history_by_params(id=history_id)
    history_job_steps = _history.get_historySteps_by_params(history=history).order_by('order')
    history_step = _history.get_historyStep_by_params(id=history_step_id)
    
    if history_step:
        list_slice = list(history_job_steps).index(history_step)
        history_job_steps = history_job_steps[list_slice:]
    
    if history.mode == enum_template.TEMPLATE_MODE_AUTO:
        _handle_job_auto(history,history_job_steps)
        
    if history.mode == enum_template.TEMPLATE_MODE_MANNUAL:
        if operation == 'execute':
            _handle_job_mannual(history,history_step)
        else:
            history_step_next = history_job_steps[0]
            history_step_next.result = enum_history.RESULT_WAIT_USER
            history_step_next.save()
        
    if history.mode == enum_template.TEMPLATE_MODE_MIX:
        history_step = history_job_steps[0]
        step_type = history_step.jobstep.step_type
        if operation != 'execute' and step_type == enum_template.STEP_TYPE_TEXT:
            history_step.result = enum_history.RESULT_WAIT_USER
            history_step.save()
        else:
            _handle_job_mix(history,history_job_steps)
    
    thread_name = 'Thread-%s'%history.id
    if thread_name in ThreadInfo.data.keys():
        del ThreadInfo.data[thread_name]

class ThreadInfo():
    data = {}

#import ctypes
#
#def _async_raise(tid,exctype):
#    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid),ctypes.py_object(exctype))
#    if res == 0:
#        raise ValueError("nonexistent thread id")
#    elif res > 1:
#        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid),0)
#        raise SystemError("PyThreadState_SetAsyncExc failed")
#    
#class JobThread(threading.Thread):
#    def __init__(self, history_id, history_step_id=0, operation=''):
#        threading.Thread.__init__(self)
#        self.history_id = history_id
#        self.history_step_id = history_step_id
#        self.operation = operation
#        
#    def run(self):
#        _handle_job(self.history_id, self.history_step_id, self.operation)
#    
#    def terminate(self):
#        self.raise_exc(SystemExit)
#        
#    def raise_exc(self,excobj):
#        assert self.isAlive(),"thread must be started"
#        for tid,tobj in threading._active.items():
#            if tobj is self:
#                _async_raise(tid,excobj)
#                return

def handle_job(job,user):
    '''
        use thread to do the actual job, return history id for page querying.
    '''
    result = pre_handle_job(job,user)
    logger.debug("pre handle job done.")
    if result['status'] == 200:
        history_id = result['result']['history_id']
        history = _history.get_history_by_params(id=history_id)

        thread = threading.Thread(target=_handle_job,args=(history.id,0,''))
#        thread = JobThread(history.id,0,'')
        thread_name = 'Thread-history-%s'%history.id
        thread.setName(thread_name)
        thread.start()
        ThreadInfo.data['%s'%thread_name] = thread

        msg = "### handle job == current threading name: {0} is handing history: {1}".format(threading.currentThread().getName(),history.id)
        logger.debug(msg)
    return result

def handle_job_schedule(job_id="", username="", task_id=""):
    """
        FOR SCHEDULE JOB CALL.
    """
    schedule_history = None
    try:
        logger.debug(
            "### start schedule job , task_id:{0}, job_id:{1}, username: {2}".format(task_id, job_id, username))
        job = _job.get_job_by_params(id=job_id)
        user = _user.get_user_by_params(username=username)
        result = handle_job(job, user)
        logger.debug("### end schedule job , task_id:{0}, result:{1}".format(task_id, result))

        schedule_history = ScheduleHistory.objects.create(task=ScheduleJobs.objects.get(id=task_id),result=enum_history.SCHEDULE_HISTORY_RESULT_TRIGGER)
        history = _history.get_history_by_params(id=result['result']['history_id'])
        history.startup_type = enum_history.HISTORY_STARTUP_TYPE_AUTO
        history.save()
        schedule_history.history = history
        if result['status'] == 200:
            schedule_history.result = enum_history.SCHEDULE_HISTORY_RESULT_SUCCESS
            schedule_history.info = u'作业启动成功'
        else:
            schedule_history.result = enum_history.SCHEDULE_HISTORY_RESULT_FAIL
            schedule_history.info = result.get("result",{}).get("msg","")
    except:
        error = traceback.format_exc()
        logger.error("### handle schedule job ERROR, QUIT.")
        logger.error(error)
    finally:
        schedule_history.save()

def get_online_status(id_list):
    #### get online status from cache.
    cached_up_agents = rc.smembers(MINIONS_UP_SET_KEY)
    online_agents = set(cached_up_agents).intersection(set(id_list))
    online_agents_num = len(online_agents)
    offline_agents_num = len(id_list)-online_agents_num
    offline_agents = set(id_list).difference(online_agents)
    
    return online_agents_num,offline_agents_num,online_agents,offline_agents

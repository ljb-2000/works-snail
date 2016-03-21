#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# --------------------------------
# Author: shenjh@snail.com
# Date: 2015/5/25
# Usage:
#  1.文件放置到 /srv/salt/_modules/下
#  2.执行salt 'syndic*' state.highstate
#--------------------------------

import sys, os
import platform
import logging
import salt.utils
import psutil,datetime
import traceback

log = logging.getLogger(__name__)

def format_bytes(num):
    '''
        format bytes
    '''
    if num / 1024.0 / 1024.0 > 1:
        return "%.2f"%(num / 1024.0 / 1024.0)+'GB'
    if num / 1024.0> 1:
        return "%.2f"%(num / 1024.0)+'MB'
    return "%.2f"%(num)+'B'

def pwd_valid(password, domain='SNAIL'):
    system = platform.system()
    state = False
    print 'platform is %s' % (system)
    if system == 'Windows':
        import win32security
        try:
            win32security.LogonUser('Administrator', domain, password, win32security.LOGON32_LOGON_NETWORK,
                                    win32security.LOGON32_PROVIDER_DEFAULT)
            state = True
        except:
            state = False
    elif system == 'Linux':
        import crypt, spwd
        entry = spwd.getspnam('root').sp_pwd
        shadows = entry.split('$')
        encrypt = crypt.crypt(password, "$%s$%s" % (shadows[1], shadows[2]))
        state = True if encrypt == entry else False
    else:
        print 'Unknown platform!'
    print 'check result is %s' % (state)
    return state

def modify_pwd(newpassword):
    system = platform.system()
    print 'platform is %s' % (system)
    if system == 'Windows':
        cmd='net user Administrator %s' %newpassword
    elif system == 'Linux':
        cmd="echo '%s'| passwd --stdin root" %newpassword
    result = os.system(cmd)
    return result
#     result = os.popen(cmd)
#     return result.read()

def status_info(types):
    check_items = set(['memory','uptime','disk'])
    types = types.split(",")
    result = {}
    is_windows = salt.utils.is_windows()
    for item in check_items:
        if item not in types:
            log.warning("ignore status collect of '{0}'".format(item))
            result.update({
                item:""
            })
            continue
        if item == 'uptime':
            if is_windows:
                result.update({item:'System Boot Time: '+datetime.datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')})
            else:
                result.update({item:__salt__['cmd.run']('uptime')})
        elif item == 'memory':
            if is_windows:
                stats = psutil.virtual_memory()
                result.update({item:'Total: %s\r\nUsed: %s\r\nFree: %s'%(format_bytes(stats.total/1024),format_bytes(stats.used/1024),format_bytes(stats.free/1024))})
            else:
                result.update({item:__salt__['cmd.run']('free -m')})
        elif item == 'disk':
            if is_windows:
                stat = __salt__['disk.usage']()
                info = []
                for disk,detail in stat.iteritems():
                    if not detail['used']:
                        continue
                    info.append(disk+' Available:'+format_bytes(detail['available'])+',  Used:'+format_bytes(detail['used']))
                    info = sorted(info)

                result.update({item:"\r\n".join(info)})
            else:
                result.update({item:__salt__['cmd.run']('df -h')})
    return result

def agent_info():
    log.info('## start to get agent_info...')
    is_windows = salt.utils.is_windows()
    try:
        config_file = 'c:/salt/conf/minion' if is_windows else '/etc/salt/minion'
        install_time = __salt__['file.lstat'](config_file).get('st_ctime','')
        version = __salt__['test.version']()
        ip_addrs = __salt__['network.ip_addrs']()
        locale_info = __salt__['grains.item']('locale_info')
        log.info('## end get agent_info.')
        return {
            'os_type': 'Windows' if is_windows else 'Linux',
            'install_time': install_time,
            'salt_version': version,
            'ip_addrs': ip_addrs,
            'locale_info': locale_info
        }
    except:
        error = traceback.format_exc()
        log.error('## error get agent_info.')
        log.error(error)
    return None

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'usage: python ujobs.py password domain ####default domain is "SNAIL"'
        exit(0)
    passwd = sys.argv[1]
    domain = 'SNAIL'
    if len(sys.argv) == 3:
        domain = sys.argv[2]
    print pwd_valid(passwd, domain)

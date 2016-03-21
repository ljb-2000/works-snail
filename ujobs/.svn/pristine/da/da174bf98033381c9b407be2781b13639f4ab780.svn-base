#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Created on 2015-5-28

@author: wx
'''

import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
# from saltclient import client
from ctranslate import LazyEncoder
import re
from releaseinfo import IP_KEY_PREFIX, DETAIL_KEY_PREFIX, MINIONS_UP_SET_KEY
from redisclient import rc
import datetime
from service import _salt
import time
from utils import send_single_api_request
import traceback

@csrf_exempt
def ajax_agent_valid(request):
    '''
        Author: wx
        Usage: only valid agent
    '''
    sdicts = {}
    
    ip_dict = {}
    iptxt = request.POST.get('iptxt')
    ip_reg = '^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$'
    minion_ip = iptxt.strip()
    
    #格式错误
    if not re.search(ip_reg, minion_ip):
        ip_dict[minion_ip] = [-2, '', '']
    else:
        minions_ups = rc.smembers(MINIONS_UP_SET_KEY)
        minion_id = rc.get(IP_KEY_PREFIX+minion_ip)
        #agent不存在
        if not rc.exists(IP_KEY_PREFIX+minion_ip):
            ip_dict[minion_ip] = [-99, '', '']
        else:
            #agent异常
            if minion_id not in list(minions_ups):
                ip_dict[minion_ip] = [-1, '', '']
            else:
                ip_dict[minion_ip] = [1, '', '']
        
    sdicts['ip_dict'] = json.dumps(ip_dict)
    return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))

@csrf_exempt
def ajax_pwd_valid(request, valid_type):
    '''
        Author: wx
        Usage: valid agent&password
        
        valid_type 0 modify password
        valid_type 1 only valid password
        valid_type 2 valid password and os
    '''
    sdicts = {}
    total = 0
    num = 0
    
    minion_ip_dict = {}
    hide_ip_dict_str = request.POST.get('hidetxt')
    hide_ip_dict = {}
    if hide_ip_dict_str:
        hide_ip_dict = json.loads(hide_ip_dict_str)
        total = hide_ip_dict.get('total')
        num = hide_ip_dict.get('num')
    
    iptxt = request.POST.get('iptxt')
    minion_info_list = iptxt.split('\n')
    ip_reg = '^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$'
    for minion_info in minion_info_list:
        minion_info_list = minion_info.strip().split(' ')
        minion_infos = []
        for item in minion_info_list:
            if item:
                minion_infos.append(item)
        minion_ip = minion_infos[0]
        if not re.search(ip_reg, minion_ip):
            continue
        minion_psw = ''
        minion_psw_new = ''
        minion_os = ''
        
        #格式错误
        if int(valid_type):
            if len(minion_infos) != 2:
                if minion_ip not in hide_ip_dict.keys():
                    total += 1
                else:
                    hide_old = hide_ip_dict[minion_ip]
                    if hide_old[0] == 1:
                        num -= 1
                hide_ip_dict[minion_ip] = [-2, minion_psw_new, minion_os]
                continue
            minion_psw = minion_infos[1]
        else:
            if len(minion_infos) != 3:
                if minion_ip not in hide_ip_dict.keys():
                    total += 1
                else:
                    hide_old = hide_ip_dict[minion_ip]
                    if hide_old[0] == 1:
                        num -= 1
                hide_ip_dict[minion_ip] = [-2, minion_psw_new, minion_os]
                continue
            minion_psw = minion_infos[1]
            minion_psw_new = minion_infos[2]
        
        #agent不存在
        if not rc.exists(IP_KEY_PREFIX+minion_ip):
            if minion_ip not in hide_ip_dict.keys():
                total += 1
            hide_ip_dict[minion_ip] = [-99, minion_psw_new, minion_os]
            continue
        
        minion_id = rc.get(IP_KEY_PREFIX+minion_ip)
        minion_os = rc.hget(DETAIL_KEY_PREFIX+minion_id,'kernel')

        # jid = client.cmd_async(minion_ip, 'ujobs.pwd_valid', [u'%s'%minion_psw], expr_form='ipcidr')
        _,jid = send_single_api_request(minion_ip, 'ujobs.pwd_valid', [u'%s'%minion_psw], expr_form='ipcidr',async=True)
        minion_ip_dict[jid] = {'minion_id':minion_id, 'minion_ip':minion_ip, 'minion_psw_new':minion_psw_new, 'minion_os':minion_os}
    
    retry = 5
    while retry>0:
        result,minion_ip_dict,total,num = get_salt_returns(minion_ip_dict,hide_ip_dict,total,num)
        if result:
            retry = -1
        else:
            retry -= 1 
            
    for minion_info in minion_ip_dict.values():
        minion_id = minion_info.get('minion_id')
        minion_ip = minion_info.get('minion_ip')
        minion_psw_new = minion_info.get('minion_psw_new')
        minion_os = minion_info.get('minion_os')
 
        #agent异常
        if minion_ip not in hide_ip_dict.keys():
            total += 1
        hide_ip_dict[minion_ip] = [-1, minion_psw_new, minion_os]
        
    hide_ip_dict['total'] = total
    hide_ip_dict['num'] = num
    sdicts['ip_dict'] = json.dumps(hide_ip_dict)
    return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))

@csrf_exempt
def ajax_pwd_valid_v2(request, valid_type):
    '''
        Author: wx
        Usage: valid agent&password
        
        valid_type 0 modify password
        valid_type 1 only valid password
        valid_type 2 valid password and os
    '''
    sdicts = {}
    total = 0
    num = 0
    
    minion_ip_dict = {}
    hide_ip_dict = {}
    
    iptxt = request.POST.get('iptxt')
    minion_info_list = iptxt.split('\n')
    ip_reg = '^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$'
    for minion_info in minion_info_list:
        minion_info_list = minion_info.strip().split(' ')
        minion_infos = []
        for item in minion_info_list:
            if item:
                minion_infos.append(item)
        minion_ip = minion_infos[0]
        if not re.search(ip_reg, minion_ip):
            continue
        minion_psw = ''
        minion_psw_new = ''
        minion_os = ''
        
        #格式错误
        if int(valid_type):
            if len(minion_infos) != 2:
                if minion_ip not in hide_ip_dict.keys():
                    total += 1
                else:
                    hide_old = hide_ip_dict[minion_ip]
                    if hide_old[0] == 1:
                        num -= 1
                hide_ip_dict[minion_ip] = [-2, minion_psw_new, minion_os, minion_ip]
                continue
            minion_psw = minion_infos[1]
        else:
            if len(minion_infos) != 3:
                if minion_ip not in hide_ip_dict.keys():
                    total += 1
                else:
                    hide_old = hide_ip_dict[minion_ip]
                    if hide_old[0] == 1:
                        num -= 1
                hide_ip_dict[minion_ip] = [-2, minion_psw_new, minion_os, minion_ip]
                continue
            minion_psw = minion_infos[1]
            minion_psw_new = minion_infos[2]
        
        #agent不存在
        if not rc.exists(IP_KEY_PREFIX+minion_ip):
            if minion_ip not in hide_ip_dict.keys():
                total += 1
            hide_ip_dict[minion_ip] = [-99, minion_psw_new, minion_os, minion_ip]
            continue
        
        minion_id = rc.get(IP_KEY_PREFIX+minion_ip)
        minion_os = rc.hget(DETAIL_KEY_PREFIX+minion_id,'kernel')

        # jid = client.cmd_async(minion_ip, 'ujobs.pwd_valid', [u'%s'%minion_psw], expr_form='ipcidr')
        _,jid = send_single_api_request(minion_ip, 'ujobs.pwd_valid', [u'%s'%minion_psw], expr_form='ipcidr',async=True)
        minion_ip_dict[jid] = {'minion_id':minion_id, 'minion_ip':minion_ip, 'minion_psw_new':minion_psw_new, 'minion_os':minion_os}
    
    retry = 5
    while retry>0:
        result,minion_ip_dict,total,num = get_salt_returns_v2(minion_ip_dict,hide_ip_dict,total,num)
        if result:
            retry = -1
        else:
            retry -= 1 
    
    #agent异常
    for minion_info in minion_ip_dict.values():
        minion_id = minion_info.get('minion_id')
        minion_ip = minion_info.get('minion_ip')
        minion_psw_new = minion_info.get('minion_psw_new')
        minion_os = minion_info.get('minion_os')
        #id未重复
        if minion_id not in hide_ip_dict.keys():    
            total += 1
            hide_ip_dict[minion_id] = [-1, minion_psw_new, minion_os, minion_ip]
        #id重复
        else:
            hide_old = hide_ip_dict[minion_id]
            minion_ip_old = hide_old[3]
            if hide_old[0] == 1:
                num -= 1
            hide_ip_dict[minion_id] = [-1, minion_psw_new, minion_os, minion_ip_old+'<br>'+minion_ip]
        
    hide_ip_dict['total'] = total
    hide_ip_dict['num'] = num
    sdicts['ip_dict'] = json.dumps(hide_ip_dict)
    return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))

def get_salt_returns(minion_ip_dict,hide_ip_dict,total,num):
    time.sleep(5)
    result = True
    for minion_key,minion_info in minion_ip_dict.items():
        minion_id = minion_info.get('minion_id')
        minion_ip = minion_info.get('minion_ip')
        minion_psw_new = minion_info.get('minion_psw_new')
        minion_os = minion_info.get('minion_os')
        salt_return = _salt.get_saltReturn_by_params(jid=minion_key,minion_id=minion_id)
        if not salt_return:
            result = False
        else:
            #ip未重复
            if minion_ip not in hide_ip_dict.keys():
                total += 1
                if salt_return.result == 'true':
                    hide_ip_dict[minion_ip] = [1, minion_psw_new, minion_os]
                    num += 1
                else:
                    hide_ip_dict[minion_ip] = [0, minion_psw_new, minion_os]
            #ip重复
            else:
                hide_old = hide_ip_dict[minion_ip]
                if salt_return.result == 'true':
                    if hide_old[0] != 1:
                        num += 1
                    hide_ip_dict[minion_ip] = [1, minion_psw_new, minion_os]
                else:
                    if hide_old[0] == 1:
                        num -= 1
                    hide_ip_dict[minion_ip] = [0, minion_psw_new, minion_os]
            del minion_ip_dict[minion_key]
    return result,minion_ip_dict,total,num

def get_salt_returns_v2(minion_ip_dict,hide_ip_dict,total,num):
    time.sleep(5)
    result = True
    for minion_key,minion_info in minion_ip_dict.items():
        minion_id = minion_info.get('minion_id')
        minion_ip = minion_info.get('minion_ip')
        minion_psw_new = minion_info.get('minion_psw_new')
        minion_os = minion_info.get('minion_os')
        salt_return = _salt.get_saltReturn_by_params(jid=minion_key,minion_id=minion_id)
        if not salt_return:
            result = False
        else:
            #id未重复
            if minion_id not in hide_ip_dict.keys():
                total += 1
                if salt_return.result == 'true':
                    hide_ip_dict[minion_id] = [1, minion_psw_new, minion_os, minion_ip]
                    num += 1
                else:
                    hide_ip_dict[minion_id] = [0, minion_psw_new, minion_os, minion_ip]
            #id重复
            else:
                hide_old = hide_ip_dict[minion_id]
                minion_ip_old = hide_old[3]
                if salt_return.result == 'true':
                    if hide_old[0] != 1:
                        num += 1
                    hide_ip_dict[minion_id] = [1, minion_psw_new, minion_os, minion_ip_old+'<br>'+minion_ip]
                else:
                    if hide_old[0] == 1:
                        num -= 1
                    hide_ip_dict[minion_id] = [0, minion_psw_new, minion_os, minion_ip_old+'<br>'+minion_ip]
            del minion_ip_dict[minion_key]
    return result,minion_ip_dict,total,num

@csrf_exempt
def ajax_cmdb_valid(request):
    '''
        Author: wx
        Usage: valid cmdb agent
    '''
    sdicts = {}
    total = 0
    num = 0
    
    hide_ip_dict = {}
    iptxt = request.POST.get('iptxt')
    minion_ip_list = iptxt.split(',')
    minions_ups = rc.smembers(MINIONS_UP_SET_KEY)
    for minion_ip in minion_ip_list:
        #agent不存在
        if not rc.exists(IP_KEY_PREFIX+minion_ip):
            if minion_ip not in hide_ip_dict.keys():
                total += 1
            hide_ip_dict[minion_ip] = [-99, '', '']
            continue
        total += 1
        minion_id = rc.get(IP_KEY_PREFIX+minion_ip)
        minion_os = rc.hget(DETAIL_KEY_PREFIX+minion_id,'kernel')
        #agent异常
        if minion_id not in list(minions_ups):
            hide_ip_dict[minion_ip] = [-2, '', minion_os]
        else:
            num += 1
            hide_ip_dict[minion_ip] = [1, '', minion_os]
        
    hide_ip_dict['total'] = total
    hide_ip_dict['num'] = num
    sdicts['ip_dict'] = json.dumps(hide_ip_dict)
    return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))

@csrf_exempt
def ajax_cmdb_valid_v2(request):
    '''
        Author: wx
        Usage: valid cmdb agent
    '''
    sdicts = {}
    total = 0
    num = 0
    
    hide_ip_dict = {}
    iptxt = request.POST.get('iptxt')
    minion_ip_list = iptxt.split(',')
    minions_ups = rc.smembers(MINIONS_UP_SET_KEY)
    for minion_ip in minion_ip_list:
        #agent不存在
        if not rc.exists(IP_KEY_PREFIX+minion_ip):
            if minion_ip not in hide_ip_dict.keys():
                total += 1
            hide_ip_dict[minion_ip] = [-99, '', '', minion_ip]
            continue
        
        minion_id = rc.get(IP_KEY_PREFIX+minion_ip)
        minion_os = rc.hget(DETAIL_KEY_PREFIX+minion_id,'kernel')
        
        #id未重复
        if minion_id not in hide_ip_dict.keys():
            #agent异常
            if minion_id not in list(minions_ups):
                total += 1
                hide_ip_dict[minion_id] = [-2, '', minion_os, minion_ip]
            else:
                total += 1
                num += 1
                hide_ip_dict[minion_id] = [1, '', minion_os, minion_ip]
        #id重复
        else:
            minion_info_old = hide_ip_dict[minion_id]
            minion_status_old = minion_info_old[0]
            minion_ip_old = minion_info_old[3]
            #agent异常
            if minion_id not in list(minions_ups):
                if minion_status_old == 1:
                    num -= 1
                hide_ip_dict[minion_id] = [-2, '', minion_os, minion_ip_old+'<br>'+minion_ip]
            else:
                if minion_status_old != 1:
                    num += 1
                hide_ip_dict[minion_id] = [1, '', minion_os, minion_ip_old+'<br>'+minion_ip]
        
    hide_ip_dict['total'] = total
    hide_ip_dict['num'] = num
    sdicts['ip_dict'] = json.dumps(hide_ip_dict)
    return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))
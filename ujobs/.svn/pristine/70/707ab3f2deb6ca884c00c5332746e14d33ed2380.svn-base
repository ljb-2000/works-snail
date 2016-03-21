#!/usr/bin/env python
# -*- coding:utf-8 -*-

# --------------------------------
# Author: shenjh@snail.com
# Date: 2015/10/14
# Usage:
# --------------------------------

import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from utils.redisclient import rc
from releaseinfo import DETAIL_KEY_PREFIX,IP_KEY_PREFIX
import traceback
import json
import logging


logger = logging.getLogger('logger_api')

@csrf_exempt
def get_agent_info(request,agent_ip):
    """
        get agent info from ip.
    """
    info = {}
    logger.debug("#### start api request call: api/get_agent_info/, IP:{0}".format(agent_ip))
    keys = ['biosversion', 'kernel', 'domain', 'kernelrelease', 'serialnumber', 'mem_total', 'SSDs', 'osrelease', 'ip6_interfaces', 'num_cpus', 'hwaddr_interfaces', 'ip4_interfaces', 'cpu_model', 'biosreleasedate', 'host', 'gpus', 'manufacturer', 'num_gpus', 'virtual', 'productname', 'osarch', 'cpuarch', 'os']
    try:
        minion_id = rc.get(IP_KEY_PREFIX+agent_ip)
        if minion_id:
            values = rc.hmget(DETAIL_KEY_PREFIX+minion_id,keys)
            json_values = []
            for value in values:
                try:
                    json_values.append(eval(value))
                except:
                    json_values.append(value)
            info =  dict(zip(keys, json_values))
    except Exception,e:
        error = traceback.format_exc()
        print error
        logger.error(error)
    logger.debug("#### api request end!")
    return HttpResponse(json.dumps(info), content_type="application/json")
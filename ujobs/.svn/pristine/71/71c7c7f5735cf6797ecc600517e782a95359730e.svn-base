#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Created on 2015-5-22

@author: wx
'''
from apps.salts.models import SaltJob, SaltReturn

import logging
logger = logging.getLogger('logger')

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def get_or_create_saltJob_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return SaltJob.objects.get_or_create(**kwargs)

def get_saltJob_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return SaltJob.objects.get(**kwargs)
    except SaltJob.DoesNotExist:
        logger.error(u"SaltJob对象不存在（%s）" % kwargs)
    except SaltJob.MultipleObjectsReturned:
        logger.error(u"SaltJob对象存在多条记录（%s）" % kwargs)
    return None

def get_saltJobs_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return SaltJob.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def get_or_create_saltReturn_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return SaltReturn.objects.get_or_create(**kwargs)

def get_saltReturn_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return SaltReturn.objects.get(**kwargs)
    except SaltReturn.DoesNotExist:
        logger.error(u"SaltReturn对象不存在（%s）" % kwargs)
    except SaltReturn.MultipleObjectsReturned:
        logger.error(u"SaltReturn对象存在多条记录（%s）" % kwargs)
    return None

def get_saltReturns_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return SaltReturn.objects.filter(**kwargs)
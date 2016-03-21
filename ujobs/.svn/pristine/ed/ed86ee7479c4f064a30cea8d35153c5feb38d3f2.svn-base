#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Created on 2015-6-1

@author: wx
'''
from apps.script.models import Script, Version

import logging
logger = logging.getLogger('logger')

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_script_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return Script.objects.create(**kwargs)

def get_or_create_script_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return Script.objects.get_or_create(**kwargs)

def get_script_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return Script.objects.get(**kwargs)
    except Script.DoesNotExist:
        logger.error(u"Script对象不存在（%s）" % kwargs)
    except Script.MultipleObjectsReturned:
        logger.error(u"Script对象存在多条记录（%s）" % kwargs)
    return None

def get_scripts_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return Script.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def get_or_create_version_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return Version.objects.get_or_create(**kwargs)

def get_version_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return Version.objects.get(**kwargs)
    except Version.DoesNotExist:
        logger.error(u"Version对象不存在（%s）" % kwargs)
    except Version.MultipleObjectsReturned:
        logger.error(u"Version对象存在多条记录（%s）" % kwargs)
    return None

def get_versions_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return Version.objects.filter(**kwargs)
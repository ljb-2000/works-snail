#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from apps.input.models import FileUpload

import logging
logger = logging.getLogger('logger')

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================
def create_fileUpload_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 创建  对象
    '''
    return FileUpload.objects.create(**kwargs)

def get_or_create_fileUpload_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return FileUpload.objects.get_or_create(**kwargs)

def get_fileUpload_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return FileUpload.objects.get(**kwargs)
    except FileUpload.DoesNotExist:
        logger.error(u"FileUpload对象不存在（%s）" % kwargs)
    except FileUpload.MultipleObjectsReturned:
        logger.error(u"FileUpload对象存在多条记录（%s）" % kwargs)
    return None

def get_fileUploads_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return FileUpload.objects.filter(**kwargs)


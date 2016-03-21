#!/usr/bin/env python
# -*- coding:utf-8 -*-

# --------------------------------
# Author: shenjh@snail.com
# Date: 2015/8/14
# Usage:
# --------------------------------

from apps.files.models import *
import logging
logger = logging.getLogger('logger')

#===============================================================================
#  for FileInfo class
#===============================================================================

def get_or_create_fileInfo_by_params(**kwargs):
    return FileInfo.objects.get_or_create(**kwargs)

def get_fileInfo_by_params(**kwargs):
    try:
        return FileInfo.objects.get(**kwargs)
    except FileInfo.DoesNotExist:
        logger.error(u"FileInfo对象不存在（%s）" % kwargs)
    except FileInfo.MultipleObjectsReturned:
        logger.error(u"FileInfo对象存在多条记录（%s）" % kwargs)
    return None

def get_fileInfos_by_params(**kwargs):
    return FileInfo.objects.filter(**kwargs)

#===============================================================================
#  for UploadRecord class
#===============================================================================

def get_or_create_uploadRecord_by_params(**kwargs):
    return UploadRecord.objects.get_or_create(**kwargs)

def get_uploadRecord_by_params(**kwargs):
    try:
        return UploadRecord.objects.get(**kwargs)
    except UploadRecord.DoesNotExist:
        logger.error(u"UploadRecord对象不存在（%s）" % kwargs)
    except UploadRecord.MultipleObjectsReturned:
        logger.error(u"UploadRecord对象存在多条记录（%s）" % kwargs)
    return None

def get_uploadRecords_by_params(**kwargs):
    return UploadRecord.objects.filter(**kwargs)

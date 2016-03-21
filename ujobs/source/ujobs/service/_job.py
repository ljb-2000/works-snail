#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Created on 2015-6-8

@author: wx
'''
from apps.jobs.models import Job, JobStep, JobStepPullFile, JobStepPushFile, JobStepScript, JobStepText, JobFileInfo, ScheduleJobs

import logging
logger = logging.getLogger('logger')

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_job_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 创建  对象
    '''
    return Job.objects.create(**kwargs)

def get_or_create_job_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return Job.objects.get_or_create(**kwargs)

def get_job_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return Job.objects.get(**kwargs)
    except Job.DoesNotExist:
        logger.error(u"Job对象不存在（%s）" % kwargs)
    except Job.MultipleObjectsReturned:
        logger.error(u"Job对象存在多条记录（%s）" % kwargs)
    return None

def get_jobs_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return Job.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================


def create_jobStep_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 创建  对象
    '''
    return JobStep.objects.create(**kwargs)

def get_or_create_jobStep_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return JobStep.objects.get_or_create(**kwargs)

def get_jobStep_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return JobStep.objects.get(**kwargs)
    except JobStep.DoesNotExist:
        logger.error(u"JobStep对象不存在（%s）" % kwargs)
    except JobStep.MultipleObjectsReturned:
        logger.error(u"JobStep对象存在多条记录（%s）" % kwargs)
    return None

def get_jobSteps_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return JobStep.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_jobStepPullFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 创建  对象
    '''
    return JobStepPullFile.objects.create(**kwargs)

def get_or_create_jobStepPullFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return JobStepPullFile.objects.get_or_create(**kwargs)

def get_jobStepPullFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return JobStepPullFile.objects.get(**kwargs)
    except JobStepPullFile.DoesNotExist:
        logger.error(u"JobStepPullFile对象不存在（%s）" % kwargs)
    except JobStepPullFile.MultipleObjectsReturned:
        logger.error(u"JobStepPullFile对象存在多条记录（%s）" % kwargs)
    return None

def get_jobStepPullFiles_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return JobStepPullFile.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_jobStepPushFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 创建  对象
    '''
    return JobStepPushFile.objects.create(**kwargs)

def get_or_create_jobStepPushFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return JobStepPushFile.objects.get_or_create(**kwargs)

def get_jobStepPushFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return JobStepPushFile.objects.get(**kwargs)
    except JobStepPushFile.DoesNotExist:
        logger.error(u"JobStepPushFile对象不存在（%s）" % kwargs)
    except JobStepPushFile.MultipleObjectsReturned:
        logger.error(u"JobStepPushFile对象存在多条记录（%s）" % kwargs)
    return None

def get_jobStepPushFiles_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return JobStepPushFile.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_jobStepScript_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 创建  对象
    '''
    return JobStepScript.objects.create(**kwargs)

def get_or_create_jobStepScript_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return JobStepScript.objects.get_or_create(**kwargs)

def get_jobStepScript_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return JobStepScript.objects.get(**kwargs)
    except JobStepScript.DoesNotExist:
        logger.error(u"JobStepScript对象不存在（%s）" % kwargs)
    except JobStepScript.MultipleObjectsReturned:
        logger.error(u"JobStepScript对象存在多条记录（%s）" % kwargs)
    return None

def get_jobStepScripts_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return JobStepScript.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_jobStepText_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 创建  对象
    '''
    return JobStepText.objects.create(**kwargs)

def get_or_create_jobStepText_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return JobStepText.objects.get_or_create(**kwargs)

def get_jobStepText_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return JobStepText.objects.get(**kwargs)
    except JobStepText.DoesNotExist:
        logger.error(u"JobStepText对象不存在（%s）" % kwargs)
    except JobStepText.MultipleObjectsReturned:
        logger.error(u"JobStepText对象存在多条记录（%s）" % kwargs)
    return None

def get_jobStepTexts_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return JobStepText.objects.filter(**kwargs)


#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def get_or_create_jobFileInfo_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return JobFileInfo.objects.get_or_create(**kwargs)

def get_jobFileInfo_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return JobFileInfo.objects.get(**kwargs)
    except JobFileInfo.DoesNotExist:
        logger.error(u"JobFileInfo对象不存在（%s）" % kwargs)
    except JobFileInfo.MultipleObjectsReturned:
        logger.error(u"JobFileInfo对象存在多条记录（%s）" % kwargs)
    return None

def get_jobFileInfos_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return JobFileInfo.objects.filter(**kwargs)

def get_scheduleJob_by_params(**kwargs):
    try:
        return ScheduleJobs.objects.get(**kwargs)
    except ScheduleJobs.DoesNotExist:
        logger.error(u"ScheduleJobs对象不存在（%s）" % kwargs)
    except ScheduleJobs.MultipleObjectsReturned:
        logger.error(u"ScheduleJobs对象存在多条记录（%s）" % kwargs)
    return None

def get_scheduleJobs_by_params(**kwargs):
    return ScheduleJobs.objects.filter(**kwargs)
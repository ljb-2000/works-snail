#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Created on 2015-6-1

@author: wx
'''
from apps.history.models import History, HistoryStep, HistoryStepPullFile, HistoryStepPushFile, HistoryStepScript, HistoryStepText, RunningResult, ScheduleHistory

import logging
logger = logging.getLogger('logger')

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_history_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 创建  对象
    '''
    return History.objects.create(**kwargs)

def get_or_create_history_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return History.objects.get_or_create(**kwargs)

def get_history_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return History.objects.get(**kwargs)
    except History.DoesNotExist:
        logger.error(u"History对象不存在（%s）" % kwargs)
    except History.MultipleObjectsReturned:
        logger.error(u"History对象存在多条记录（%s）" % kwargs)
    return None

def get_historys_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return History.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def get_or_create_historyStep_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return HistoryStep.objects.get_or_create(**kwargs)

def get_historyStep_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return HistoryStep.objects.get(**kwargs)
    except HistoryStep.DoesNotExist:
        logger.error(u"HistoryStep对象不存在（%s）" % kwargs)
    except HistoryStep.MultipleObjectsReturned:
        logger.error(u"HistoryStep对象存在多条记录（%s）" % kwargs)
    return None

def get_historySteps_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return HistoryStep.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_historyStepPullFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 创建  对象
    '''
    return HistoryStepPullFile.objects.create(**kwargs)

def get_or_create_historyStepPullFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return HistoryStepPullFile.objects.get_or_create(**kwargs)

def get_historyStepPullFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return HistoryStepPullFile.objects.get(**kwargs)
    except HistoryStepPullFile.DoesNotExist:
        logger.error(u"HistoryStepPullFile对象不存在（%s）" % kwargs)
    except HistoryStepPullFile.MultipleObjectsReturned:
        logger.error(u"HistoryStepPullFile对象存在多条记录（%s）" % kwargs)
    return None

def get_historyStepPullFiles_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return HistoryStepPullFile.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_historyStepPushFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 创建  对象
    '''
    return HistoryStepPushFile.objects.create(**kwargs)

def get_or_create_historyStepPushFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return HistoryStepPushFile.objects.get_or_create(**kwargs)

def get_historyStepPushFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return HistoryStepPushFile.objects.get(**kwargs)
    except HistoryStepPushFile.DoesNotExist:
        logger.error(u"HistoryStepPushFile对象不存在（%s）" % kwargs)
    except HistoryStepPushFile.MultipleObjectsReturned:
        logger.error(u"HistoryStepPushFile对象存在多条记录（%s）" % kwargs)
    return None

def get_historyStepPushFiles_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return HistoryStepPushFile.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_historyStepScript_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 创建  对象
    '''
    return HistoryStepScript.objects.create(**kwargs)

def get_or_create_historyStepScript_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return HistoryStepScript.objects.get_or_create(**kwargs)

def get_historyStepScript_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return HistoryStepScript.objects.get(**kwargs)
    except HistoryStepScript.DoesNotExist:
        logger.error(u"HistoryStepScript对象不存在（%s）" % kwargs)
    except HistoryStepScript.MultipleObjectsReturned:
        logger.error(u"HistoryStepScript对象存在多条记录（%s）" % kwargs)
    return None

def get_historyStepScripts_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return HistoryStepScript.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_historyStepText_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 创建  对象
    '''
    return HistoryStepText.objects.create(**kwargs)

def get_or_create_historyStepText_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return HistoryStepText.objects.get_or_create(**kwargs)

def get_historyStepText_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return HistoryStepText.objects.get(**kwargs)
    except HistoryStepText.DoesNotExist:
        logger.error(u"HistoryStepText对象不存在（%s）" % kwargs)
    except HistoryStepText.MultipleObjectsReturned:
        logger.error(u"HistoryStepText对象存在多条记录（%s）" % kwargs)
    return None

def get_historyStepTexts_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return HistoryStepText.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def get_or_create_runningResult_by_params(**kwargs):
    return RunningResult.objects.get_or_create(**kwargs)

def get_runningResult_by_params(**kwargs):
    try:
        return RunningResult.objects.get(**kwargs)
    except RunningResult.DoesNotExist:
        logger.error(u"RunningResult对象不存在（%s）" % kwargs)
    except RunningResult.MultipleObjectsReturned:
        logger.error(u"RunningResult对象存在多条记录（%s）" % kwargs)
    return None

def get_runningResults_by_params(**kwargs):
    return RunningResult.objects.filter(**kwargs)

def get_scheduleHistorys_by_params(**kwargs):
    return ScheduleHistory.objects.filter(**kwargs)
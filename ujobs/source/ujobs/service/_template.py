#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Created on 2015-6-8

@author: wx
'''
from apps.template.models import Template, TemplateStep, TemplateStepPullFile,\
    TemplateStepPushFile, TemplateStepScript, TemplateStepText, TemplateFileInfo

import logging
logger = logging.getLogger('logger')

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================
def create_template_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return Template.objects.create(**kwargs)

def get_or_create_template_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return Template.objects.get_or_create(**kwargs)

def get_template_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return Template.objects.get(**kwargs)
    except Template.DoesNotExist:
        logger.error(u"Template对象不存在（%s）" % kwargs)
    except Template.MultipleObjectsReturned:
        logger.error(u"Template对象存在多条记录（%s）" % kwargs)
    return None

def get_templates_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return Template.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_templateStep_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return TemplateStep.objects.create(**kwargs)

def get_or_create_templateStep_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return TemplateStep.objects.get_or_create(**kwargs)

def get_templateStep_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return TemplateStep.objects.get(**kwargs)
    except TemplateStep.DoesNotExist:
        logger.error(u"TemplateStep对象不存在（%s）" % kwargs)
    except TemplateStep.MultipleObjectsReturned:
        logger.error(u"TemplateStep对象存在多条记录（%s）" % kwargs)
    return None

def get_templateSteps_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return TemplateStep.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_templateStepPullFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return TemplateStepPullFile.objects.create(**kwargs)

def get_or_create_templateStepPullFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return TemplateStepPullFile.objects.get_or_create(**kwargs)

def get_templateStepPullFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return TemplateStepPullFile.objects.get(**kwargs)
    except TemplateStepPullFile.DoesNotExist:
        logger.error(u"TemplateStepPullFile对象不存在（%s）" % kwargs)
    except TemplateStepPullFile.MultipleObjectsReturned:
        logger.error(u"TemplateStepPullFile对象存在多条记录（%s）" % kwargs)
    return None

def get_templateStepPullFiles_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return TemplateStepPullFile.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_templateStepPushFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return TemplateStepPushFile.objects.create(**kwargs)

def get_or_create_templateStepPushFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return TemplateStepPushFile.objects.get_or_create(**kwargs)

def get_templateStepPushFile_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return TemplateStepPushFile.objects.get(**kwargs)
    except TemplateStepPushFile.DoesNotExist:
        logger.error(u"TemplateStepPushFile对象不存在（%s）" % kwargs)
    except TemplateStepPushFile.MultipleObjectsReturned:
        logger.error(u"TemplateStepPushFile对象存在多条记录（%s）" % kwargs)
    return None

def get_templateStepPushFiles_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return TemplateStepPushFile.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_templateStepScript_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return TemplateStepScript.objects.create(**kwargs)

def get_or_create_templateStepScript_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return TemplateStepScript.objects.get_or_create(**kwargs)

def get_templateStepScript_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return TemplateStepScript.objects.get(**kwargs)
    except TemplateStepScript.DoesNotExist:
        logger.error(u"TemplateStepScript对象不存在（%s）" % kwargs)
    except TemplateStepScript.MultipleObjectsReturned:
        logger.error(u"TemplateStepScript对象存在多条记录（%s）" % kwargs)
    return None

def get_templateStepScripts_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return TemplateStepScript.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_templateStepText_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return TemplateStepText.objects.create(**kwargs)

def get_or_create_templateStepText_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return TemplateStepText.objects.get_or_create(**kwargs)

def get_templateStepText_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return TemplateStepText.objects.get(**kwargs)
    except TemplateStepText.DoesNotExist:
        logger.error(u"TemplateStepText对象不存在（%s）" % kwargs)
    except TemplateStepText.MultipleObjectsReturned:
        logger.error(u"TemplateStepText对象存在多条记录（%s）" % kwargs)
    return None

def get_templateStepTexts_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return TemplateStepText.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def get_or_create_templateFileInfo_by_params(**kwargs):
    return TemplateFileInfo.objects.get_or_create(**kwargs)

def get_templateFileInfo_by_params(**kwargs):
    try:
        return TemplateFileInfo.objects.get(**kwargs)
    except TemplateFileInfo.DoesNotExist:
        logger.error(u"TemplateFileInfo对象不存在（%s）" % kwargs)
    except TemplateFileInfo.MultipleObjectsReturned:
        logger.error(u"TemplateFileInfo对象存在多条记录（%s）" % kwargs)
    return None

def get_templateFileInfos_by_params(**kwargs):
    return TemplateFileInfo.objects.filter(**kwargs)
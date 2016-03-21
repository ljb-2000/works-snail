#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from enums.enum_user import CONTENTTYPE_NAME, CONTENTTYPE_APP_LABEL, CONTENTTYPE_MODEL

import logging
logger = logging.getLogger('logger')

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def get_or_create_user_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return User.objects.get_or_create(**kwargs)

def get_user_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return User.objects.get(**kwargs)
    except User.DoesNotExist:
        logger.error(u"Account对象不存在（%s）" % kwargs)
    except User.MultipleObjectsReturned:
        logger.error(u"Account对象存在多条记录（%s）" % kwargs)
    return None

def get_users_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return User.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def get_or_create_group_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return Group.objects.get_or_create(**kwargs)

def get_group_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return Group.objects.get(**kwargs)
    except Group.DoesNotExist:
        logger.error(u"Group对象不存在（%s）" % kwargs)
    except Group.MultipleObjectsReturned:
        logger.error(u"Group对象存在多条记录（%s）" % kwargs)
    return None

def get_groups_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return Group.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def get_or_create_permission_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return Permission.objects.get_or_create(**kwargs)

def get_permission_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return Permission.objects.get(**kwargs)
    except Permission.DoesNotExist:
        logger.error(u"Permission对象不存在（%s）" % kwargs)
    except Permission.MultipleObjectsReturned:
        logger.error(u"Permission对象存在多条记录（%s）" % kwargs)
    return None

def get_permissions_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return Permission.objects.filter(**kwargs)

#===============================================================================
# 其他一些获取数据的方法
#===============================================================================

def get_custom_contenttype():
    '''
    @return: 获取自定义ContentType对象
    @note: 没有找到则会新建一个
    '''
    return ContentType.objects.get_or_create(name=CONTENTTYPE_NAME,
                                             app_label=CONTENTTYPE_APP_LABEL,
                                             model=CONTENTTYPE_MODEL)[0]

def check_custom_perm(user, perm):
    '''
    @param user: 用户
    @param perm: 权限名（可不带custom.前缀）
    @return: 返回权限检查结果bool
    '''
    if "%s." % CONTENTTYPE_APP_LABEL in perm:
        return user.has_perm(perm)
    else:
        return user.has_perm("%s.%s" % (CONTENTTYPE_APP_LABEL, perm))

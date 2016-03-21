#!/usr/bin/python
# -*- coding:utf-8 -*-
from apps.question.models import Product ,Question

import logging
logger = logging.getLogger('logger')

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_product_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return Product.objects.create(**kwargs)

def get_or_create_product_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return Product.objects.get_or_create(**kwargs)

def get_product_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return Product.objects.get(**kwargs)
    except Product.DoesNotExist:
        logger.error(u"Product对象不存在（%s）" % kwargs)
    except Product.MultipleObjectsReturned:
        logger.error(u"Product对象存在多条记录（%s）" % kwargs)
    return None

def get_products_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return Product.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_question_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return Question.objects.create(**kwargs)

def get_or_create_question_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return Question.objects.get_or_create(**kwargs)

def get_question_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return Question.objects.get(**kwargs)
    except Question.DoesNotExist:
        logger.error(u"Product对象不存在（%s）" % kwargs)
    except Question.MultipleObjectsReturned:
        logger.error(u"Product对象存在多条记录（%s）" % kwargs)
    return None

def get_questions_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return Question.objects.filter(**kwargs)
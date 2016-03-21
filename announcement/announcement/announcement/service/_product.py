#!/usr/bin/python
# -*- coding:utf-8 -*-
from apps.product.models import Product, ProductInfo, FileUploadLog, FtpUploadLog

import logging
logger = logging.getLogger('logger')

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

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

def create_productInfo_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return ProductInfo.objects.create(**kwargs)

def get_or_create_productInfo_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return ProductInfo.objects.get_or_create(**kwargs)

def get_productInfo_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: obj或None
    @note: 获取  对象
    '''
    try:
        return ProductInfo.objects.get(**kwargs)
    except ProductInfo.DoesNotExist:
        logger.error(u"ProductInfo对象不存在（%s）" % kwargs)
    except ProductInfo.MultipleObjectsReturned:
        logger.error(u"ProductInfo对象存在多条记录（%s）" % kwargs)
    return None

def get_productInfos_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: [obj,]
    @note: 获取  对象列表
    '''
    return ProductInfo.objects.filter(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_fileUploadLog_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return FileUploadLog.objects.create(**kwargs)

#===============================================================================
# Model的直接操作方法，get_or_create、get、filter 等。
#===============================================================================

def create_ftpUploadLog_by_params(**kwargs):
    '''
    @param kwargs: key=value 的键值对
    @return: 元组(obj,boolean)
    @note: 获取或创建  对象
    '''
    return FtpUploadLog.objects.create(**kwargs)
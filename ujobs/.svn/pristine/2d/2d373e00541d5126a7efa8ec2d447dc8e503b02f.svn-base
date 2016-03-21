#!/usr/bin/python
# -*- coding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _

'''
Created on 2015-5-15

@author: wx
'''


#账号类型
ACCOUNT_TYPE1 = 1
ACCOUNT_TYPE2 = 2

ACCOUNT_TYPE_CHOICES = (
     (ACCOUNT_TYPE1, _(u'类型1')),
     (ACCOUNT_TYPE2, _(u'类型2')),
)

#类型
PERM_PTYPE_TEMPLATE = 1
PERM_PTYPE_JOB = 2
PERM_PTYPE_SCRIPT = 3

PTYPE_CHOICES = (
     (PERM_PTYPE_TEMPLATE, _(u'模板')),
     (PERM_PTYPE_JOB, _(u'作业')),
     (PERM_PTYPE_SCRIPT, _(u'脚本')),
)

# for query dic map
PERM_PTYPE_MAP = {
    'template': PERM_PTYPE_TEMPLATE,
    'job': PERM_PTYPE_JOB,
    'script': PERM_PTYPE_SCRIPT,
}

#权限类型,保留
PERMISSION_SHOW = 1
PERMISSION_DELETE = 2
PERMISSION_MODIFY = 4
PERMISSION_ALL = 8

PERMISSION_TYPE_CHOICES = (
     (PERMISSION_ALL, _(u'完整权限')),
     (PERMISSION_SHOW, _(u'展示权限')),
     (PERMISSION_DELETE, _(u'删除权限')),
     (PERMISSION_MODIFY, _(u'修改权限')),
)
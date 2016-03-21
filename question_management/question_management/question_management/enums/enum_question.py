#!/usr/bin/python
# -*- coding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _

'''
Created on 2015-10-21

@author: wx
'''


#问题状态
STATUS_OPEN = 0
STATUS_CLOSE = 1

QUESTION_STATUS_CHOICES = (
     (STATUS_OPEN, u'open'),
     (STATUS_CLOSE, u'close'),
)

#问题级别
LEVEL_CRITICAL = 1
LEVEL_NORMAL = 2
LEVEL_SLIGHT = 3

QUESTION_LEVEL_CHOICES = (
     (LEVEL_CRITICAL, u'严重'),
     (LEVEL_NORMAL, u'一般'),
     (LEVEL_SLIGHT, u'轻微'),
)

#问题类型
TYPE_1 = 1
TYPE_2 = 2
TYPE_3 = 3
TYPE_4 = 4

QUESTION_TYPE_CHOICES = (
     (TYPE_1, u'硬件'),
     (TYPE_2, u'IDC环境'),
     (TYPE_3, u'系统及软件'),
     (TYPE_4, u'应用程序'),
)

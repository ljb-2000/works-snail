#!/usr/bin/python
# -*- coding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _

'''
Created on 2015-5-13

@author: wx
'''

#脚本类型
SCIPT_TYPE1 = 1 #shell
SCIPT_TYPE2 = 2 #bat
SCIPT_TYPE3 = 3 #python

SCIPT_TYPE_DICT = {
    SCIPT_TYPE1: 'sh',
    SCIPT_TYPE2: 'bat',
    SCIPT_TYPE3: 'py',
}

SCIPT_TYPE_CHOICES = (
     (SCIPT_TYPE1, _(u'shell')),
     (SCIPT_TYPE2, _(u'bat')),
     (SCIPT_TYPE3, _(u'python')),
)

#版本状态
VERSION_OPEN = 0
VERSION_CLOSE = 1

VERSION_STATUS_CHOICES = (
     (VERSION_OPEN, _(u'公开')),
     (VERSION_CLOSE, _(u'私有')),
)

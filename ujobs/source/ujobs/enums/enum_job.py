#!/usr/bin/python
# -*- coding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _

'''
Created on 2015-5-15

@author: wx
'''


#作业状态
STATUS0 = 0
STATUS1 = 1
STATUS2 = 2
STATUS3 = 3
# STATUS4 = 4

JOB_STATUS_CHOICES = (
     (STATUS0, _(u'未执行')),
     (STATUS1, _(u'执行成功')),
     (STATUS2, _(u'执行失败')),
     (STATUS3, _(u'执行中')),
     # (STATUS4, _(u'执行完成')),
)

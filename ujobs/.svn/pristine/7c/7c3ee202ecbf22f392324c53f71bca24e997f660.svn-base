#!/usr/bin/python
# -*- coding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _

'''
Created on 2015-5-14

@author: wx
'''

#模板类型
TEMPLATE_TYPE0 = 0 #未分类
TEMPLATE_TYPE1 = 1 #运营发布
TEMPLATE_TYPE2 = 2 #故障处理
TEMPLATE_TYPE3 = 3 #常用工具
TEMPLATE_TYPE4 = 4 #测试专用
TEMPLATE_TYPE97 = 97 #批量重启
TEMPLATE_TYPE98 = 98 #批量改密
TEMPLATE_TYPE99 = 99 #一次性脚本
TEMPLATE_TYPE100 = 100 #一次性传文件

USER_TEMPLATE_TYPES = (
     (TEMPLATE_TYPE0, _(u'未分类')),
     (TEMPLATE_TYPE1, _(u'运营发布')),
     (TEMPLATE_TYPE2, _(u'故障处理')),
     (TEMPLATE_TYPE3, _(u'常用工具')),
     (TEMPLATE_TYPE4, _(u'测试专用')),
)
SYSTEM_TEMPLATE_TYPES = (
    (TEMPLATE_TYPE97, _(u'批量重启')),
    (TEMPLATE_TYPE98, _(u'批量改密')),
    (TEMPLATE_TYPE99, _(u'一次性脚本')),
    (TEMPLATE_TYPE100, _(u'一次性传文件')),
)

TEMPLATE_TYPE_CHOICES = USER_TEMPLATE_TYPES + SYSTEM_TEMPLATE_TYPES

#执行模式
TEMPLATE_MODE_AUTO = 1 #无人模式
TEMPLATE_MODE_MANNUAL = 2 #单步模式
TEMPLATE_MODE_MIX = 3 #混合模式

TEMPLATE_MODE_CHOICES = (
     (TEMPLATE_MODE_AUTO, _(u'无人模式')),
     (TEMPLATE_MODE_MANNUAL, _(u'单步模式')),
     (TEMPLATE_MODE_MIX, _(u'混合模式')),
)

#步骤类型
STEP_TYPE_SCRIPT = 1 #执行脚本
STEP_TYPE_PUSH_FILE = 2 #分发文件
STEP_TYPE_PULL_FILE = 3 #拉取文件
STEP_TYPE_TEXT = 4 #文本步骤
STEP_TYPE_RESTART = 5 #批量重启
STEP_TYPE_CHANGE_PWD = 6 #批量改密

STEP_TYPE_CHOICES = (
     (STEP_TYPE_SCRIPT, _(u'执行脚本')),
     (STEP_TYPE_PUSH_FILE, _(u'分发文件')),
     (STEP_TYPE_PULL_FILE, _(u'拉取文件')),
     (STEP_TYPE_TEXT, _(u'文本步骤')),
     (STEP_TYPE_RESTART, _(u'批量重启')),
     (STEP_TYPE_CHANGE_PWD, _(u'批量改密')),
)

UPLOAD_TYPE_LOCAL = 1
UPLOAD_TYPE_REMOTE = 2

UPLOAD_TYPE_CHOICES = (
     (UPLOAD_TYPE_LOCAL, _(u'本地文件')),
     (UPLOAD_TYPE_REMOTE, _(u'远程文件')),
)

# constant value for schedule jobs.
SCHEDULE_STATUS_DELETE = 0
SCHEDULE_STATUS_PAUSE = 1
SCHEDULE_STATUS_STARTED = 2
SCHEDULE_STATUS_FINISHED = 3

SCHEDULE_STATUS_CHOICES = (
     (SCHEDULE_STATUS_DELETE, _(u'已删除')),
     (SCHEDULE_STATUS_PAUSE, _(u'已暂停')),
     (SCHEDULE_STATUS_STARTED, _(u'已启动')),
     (SCHEDULE_STATUS_FINISHED, _(u'已完成')),
)
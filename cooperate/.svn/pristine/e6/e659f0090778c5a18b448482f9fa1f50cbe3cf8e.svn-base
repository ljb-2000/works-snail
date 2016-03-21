#encoding:utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from audit_log.models.managers import AuditLog
from apps.report.models import Department

STATUS_OPEN = 0
STATUS_CLOSE = 1

ROUTINE_STATUS = (
     (STATUS_OPEN, _(u'未完成')),
     (STATUS_CLOSE, _(u'已完成')),
)

class Routine(models.Model):
    '''
    @note: 部门事务
    '''
    department = models.ForeignKey(Department, verbose_name=_(u'部门'))
    content = models.TextField(verbose_name=_(u'内容'), blank=True, null=True)
    status = models.IntegerField(verbose_name=_(u'进度'), choices=ROUTINE_STATUS, default=STATUS_OPEN)
    create_user = models.ForeignKey(User, verbose_name=_(u'创建人'), related_name='routine_create_user', blank=True, null=True)
    update_user = models.ForeignKey(User, verbose_name=_(u'更新人'), related_name='routine_update_user', blank=True, null=True)
    created = models.DateTimeField(verbose_name=_(u"创建时间"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_(u"更新时间"), auto_now=True)
    
    def __unicode__(self):
        return '%s:%s'%(self.department,self.content)
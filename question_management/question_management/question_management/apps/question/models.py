#encoding:utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from audit_log.models.managers import AuditLog
from enums import enum_question

class Product(models.Model):
    name = models.CharField(max_length=128, verbose_name=_(u'业务名称'))
    created = models.DateTimeField(verbose_name=_(u"创建时间"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_(u"更新时间"), auto_now=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')   
        
class Question(models.Model):
    '''
    @note: 问题
    '''
    product = models.ForeignKey(Product, verbose_name=_(u'业务'))
    qtime = models.DateTimeField(verbose_name=_(u"发现时间"), blank=True, null=True)
    status = models.IntegerField(verbose_name=_(u'问题状态'), choices=enum_question.QUESTION_STATUS_CHOICES, default=enum_question.STATUS_OPEN)
    level = models.IntegerField(verbose_name=_(u'问题级别'), choices=enum_question.QUESTION_LEVEL_CHOICES, default=enum_question.LEVEL_CRITICAL)
    qtype = models.IntegerField(verbose_name=_(u'问题类型'), choices=enum_question.QUESTION_TYPE_CHOICES, blank=True, null=True)
    
    title = models.CharField(max_length=50, verbose_name=_(u'标题'), blank=True, null=True)
    describe = models.TextField(max_length=1500, verbose_name=_(u'问题描述'), blank=True, null=True)
    reason = models.TextField(max_length=1500, verbose_name=_(u'问题原因'), blank=True, null=True)
    solution = models.TextField(max_length=1500, verbose_name=_(u'解决措施'), blank=True, null=True)
    
    create_user = models.ForeignKey(User, verbose_name=_(u'创建人'), blank=True, null=True)
    created = models.DateTimeField(verbose_name=_(u"创建时间"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_(u"更新时间"), auto_now=True)
    audit_log = AuditLog()

    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')      
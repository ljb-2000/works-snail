#encoding:utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from enums import enum_account
from audit_log.models.managers import AuditLog
from django.contrib.auth.models import User

'''
Created on 2015-5-15

@author: wx
'''

class Account(models.Model):
    '''
    @note: 账号
    '''
    name = models.CharField(max_length=128, verbose_name=_(u'账号名称'))
    name_abbr = models.CharField(max_length=128, verbose_name=_(u'账号别名'))
    password = models.CharField(max_length=128, verbose_name=_(u'密码'))
    account_type = models.IntegerField(verbose_name=_(u'账号类型'), choices=enum_account.ACCOUNT_TYPE_CHOICES, blank=True, null=True)
    remarks = models.CharField(max_length=256, verbose_name=_(u'备注'), blank=True, null=True)
    create_user = models.ForeignKey(User, verbose_name=_(u'创建人'), related_name='account_create_user', blank=True, null=True)
#     create_user = models.CharField(max_length=256, verbose_name=_(u'创建人'), blank=True, null=True)
    update_user = models.ForeignKey(User, verbose_name=_(u'更新人'), related_name='account_update_user', blank=True, null=True)
#     update_user = models.CharField(max_length=256, verbose_name=_(u'更新人'), blank=True, null=True)
    created = models.DateTimeField(verbose_name=_(u"创建时间"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_(u"更新时间"), auto_now=True)
    is_delete = models.BooleanField(verbose_name=_(u'是否删除'), default=False)
    audit_log = AuditLog()

    def __unicode__(self):
        return self.name
    
    class Meta: #账号
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')      
        
class Perm(models.Model):
    '''
    @note: 权限
    '''
    ptype = models.IntegerField(verbose_name=_(u'类型'), choices=enum_account.PTYPE_CHOICES, blank=True, null=True)
    object_id = models.IntegerField(verbose_name=_(u'对象id'))
    permission_type = models.IntegerField(verbose_name=_(u'权限类型'), choices=enum_account.PERMISSION_TYPE_CHOICES, blank=True, null=True,default=enum_account.PERMISSION_ALL)
    create_user = models.ForeignKey(User, verbose_name=_(u'授权人'), related_name='perm_create_user', blank=True, null=True)
    update_user = models.ForeignKey(User, verbose_name=_(u'更新人'), related_name='perm_update_user', blank=True, null=True)
    to_user = models.ForeignKey(User, verbose_name=_(u'目标用户'), related_name='perm_to_user',blank=True, null=True)
    created = models.DateTimeField(verbose_name=_(u"授予时间"), auto_now_add=True,blank=True,null=True)
    updated = models.DateTimeField(verbose_name=_(u"更新时间"), auto_now=True,blank=True,null=True)
    end_time = models.DateTimeField(verbose_name=_(u"到期时间"),blank=True,null=True)
    is_delete = models.BooleanField(verbose_name=_(u'是否删除'), default=False)
    audit_log = AuditLog()

    def __unicode__(self):
        return self.get_ptype_display()+": "+ str(self.object_id)+' from ' +self.create_user.username+ ' to ' +self.to_user.username
    
    class Meta: #权限
        verbose_name = _('Perm')
        verbose_name_plural = _('Perms')

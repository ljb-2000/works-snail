#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from enums import enum_template
from apps.accounts.models import Account
from audit_log.models.managers import AuditLog

# Create your models here.


class FileInfo(models.Model):
    '''
        上传文件信息
    '''
    def __unicode__(self):
        return self.file_name

    class Meta: #作业
        verbose_name = _('FileInfo')
        verbose_name_plural = _('FileInfo')

    file_name = models.CharField(max_length=255,verbose_name=_(u'文件名'))
    size = models.FloatField(verbose_name=_(u'大小'))
    md5sum = models.CharField(max_length=255, verbose_name=_(u'MD5值'),db_index=True)
    path = models.FilePathField(verbose_name=_(u'文件路径'))
    upload_time = models.DateTimeField(verbose_name=_(u"添加时间"), auto_now_add=True)
    audit_log = AuditLog()

class UploadRecord(models.Model):
    '''
        用户上传记录
    '''
    def __unicode__(self):
        return self.user_name+' upload file '+self.file_name

    user_name = models.CharField(max_length=128,verbose_name=_(u'用户名'))
    fileinfo = models.ForeignKey(FileInfo,verbose_name=_(u'上传文件'))
    file_name = models.CharField(max_length=256,verbose_name=_(u'文件名'))
    upload_time = models.DateTimeField(verbose_name=_(u"上传时间"), auto_now_add=True)
    src_ip = models.IPAddressField(verbose_name=u"上传IP",blank=True,null=True)
    location_type = models.IntegerField(max_length=32,verbose_name=_(u'上传类型'),choices=enum_template.UPLOAD_TYPE_CHOICES,default=enum_template.UPLOAD_TYPE_LOCAL)
    remote_path = models.FilePathField(verbose_name=_(u'远程文件路径'),blank=True,null=True)
    remote_account = models.ForeignKey(Account, verbose_name=_(u'远程账户'), blank=True, null=True)
    audit_log = AuditLog()
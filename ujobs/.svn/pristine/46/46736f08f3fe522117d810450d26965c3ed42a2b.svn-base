#encoding:utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from enums import enum_script
from audit_log.models.managers import AuditLog
from django.contrib.auth.models import User

'''
Created on 2015-5-13

@author: wx
'''

class Script(models.Model):
    '''
    @note: 脚本
    '''
    name = models.CharField(max_length=128, verbose_name=_(u'脚本名称'))
    script_type = models.IntegerField(verbose_name=_(u'脚本类型'), choices=enum_script.SCIPT_TYPE_CHOICES, default=enum_script.SCIPT_TYPE1)
    describe = models.CharField(max_length=256, verbose_name=_(u'功能描述'), blank=True, null=True)
    parameter_type = models.CharField(max_length=256, verbose_name=_(u'参数类型'), blank=True, null=True)
    create_user = models.ForeignKey(User, verbose_name=_(u'创建人'), related_name='script_create_user', blank=True, null=True)
#    create_user = models.CharField(max_length=256, verbose_name=_(u'创建人'), blank=True, null=True)
    update_user = models.ForeignKey(User, verbose_name=_(u'更新人'), related_name='script_update_user', blank=True, null=True)
#    update_user = models.CharField(max_length=256, verbose_name=_(u'更新人'), blank=True, null=True)
    created = models.DateTimeField(verbose_name=_(u"创建时间"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_(u"更新时间"), auto_now=True)
    is_delete = models.BooleanField(verbose_name=_(u'是否删除'), default=False)
    is_once = models.BooleanField(verbose_name=_(u'一次性脚本'), default=False)
    audit_log = AuditLog()

    def __unicode__(self):
        return self.name

    class Meta: #脚本
        verbose_name = _('Script')
        verbose_name_plural = _('Scripts')
        
class Version(models.Model):
    '''
    @note: 版本
    '''
    script = models.ForeignKey(Script, verbose_name=_(u'脚本'))
    name = models.CharField(max_length=128, verbose_name=_(u'版本名称'))
#    sfile = models.FileField(verbose_name=_(u'脚本文件'), upload_to=upload_file_path, blank=True, null=True)
    sfile = models.FilePathField(verbose_name=_(u'脚本文件'), blank=True, null=True)
    status = models.IntegerField(verbose_name=_(u'版本状态'), choices=enum_script.VERSION_STATUS_CHOICES, default=enum_script.VERSION_OPEN)
    remarks = models.CharField(max_length=256, verbose_name=_(u'备注'), blank=True, null=True)
    created = models.DateTimeField(verbose_name=_(u"创建时间"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_(u"更新时间"), auto_now=True)
    is_delete = models.BooleanField(verbose_name=_(u'是否删除'), default=False)
    audit_log = AuditLog()

    def __unicode__(self):
        return self.name

    class Meta: #版本
        verbose_name = _('Version')
        verbose_name_plural = _('Versions')

#replaceuploadchar = ['%20', ' ', '(', ')', '!'] 
#def upload_file_path(inst, filename):
#    for c in replaceuploadchar:
#        filename = filename.replace(c, '_')
#    index = inst.id % 100
#    return u'file/script_%d/%s' % (index, filename)
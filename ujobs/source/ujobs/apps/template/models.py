#encoding:utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from enums import enum_template
from apps.accounts.models import Account
from apps.script.models import Version
from audit_log.models.managers import AuditLog
from django.contrib.auth.models import User
from apps.files.models import UploadRecord

'''
Created on 2015-5-14

@author: wx
'''

class Template(models.Model): 
    '''
    @note: 模板
    '''
    name = models.CharField(max_length=128, verbose_name=_(u'模板名称'), blank=True, null=True)
    template_type = models.IntegerField(verbose_name=_(u'模板类型'), choices=enum_template.TEMPLATE_TYPE_CHOICES, default=enum_template.TEMPLATE_TYPE0)
    work_type = models.CharField(max_length=256, verbose_name=_(u'业务类型'), blank=True, null=True)
    remarks = models.CharField(max_length=256, verbose_name=_(u'备注'), blank=True, null=True)
    create_user = models.ForeignKey(User, verbose_name=_(u'创建人'), related_name='template_create_user', blank=True, null=True)
#    create_user = models.CharField(max_length=256, verbose_name=_(u'创建人'), blank=True, null=True)
    update_user = models.ForeignKey(User, verbose_name=_(u'更新人'), related_name='template_update_user', blank=True, null=True)
#    update_user = models.CharField(max_length=256, verbose_name=_(u'更新人'), blank=True, null=True)
    created = models.DateTimeField(verbose_name=_(u"创建时间"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_(u"更新时间"), auto_now=True)
    mode = models.IntegerField(verbose_name=_(u'执行模式'), choices=enum_template.TEMPLATE_MODE_CHOICES, default=enum_template.TEMPLATE_MODE_MANNUAL, blank=True, null=True)
    account = models.ForeignKey(Account, verbose_name=_(u'常用账户'), blank=True, null=True)
    target = models.TextField(verbose_name=_(u'目标机器'), blank=True, null=True)
    is_delete = models.BooleanField(verbose_name=_(u'是否删除'), default=False)
    audit_log = AuditLog()

    def __unicode__(self):
        return self.name
    

    class Meta: #模板
        verbose_name = _('Template')
        verbose_name_plural = _('Templates')
        
class TemplateStep(models.Model):
    '''
    @note: 模板步骤
    '''
    template = models.ForeignKey(Template, verbose_name=_(u'模板'))
    name = models.CharField(max_length=128, verbose_name=_(u'步骤名称'), blank=True, null=True)
    describe = models.CharField(max_length=256, verbose_name=_(u'步骤描述'), blank=True, null=True,default="")
    step_type = models.IntegerField(verbose_name=_(u'步骤类型'), choices=enum_template.STEP_TYPE_CHOICES, default=enum_template.STEP_TYPE_SCRIPT)
    order = models.IntegerField(verbose_name=_(u'步骤顺序'), blank=True, null=True)
    is_setting = models.BooleanField(verbose_name=_(u'单独设定'), default=False)
    account = models.ForeignKey(Account, verbose_name=_(u'常用账户'), blank=True, null=True)
    target = models.TextField(verbose_name=_(u'目标机器'), blank=True, null=True)
    is_checked = models.BooleanField(verbose_name=_(u'是否勾选'), default=True)
    is_delete = models.BooleanField(verbose_name=_(u'是否删除'), default=False)
    audit_log = AuditLog()

    def __unicode__(self):
        return self.name

    class Meta: #模板步骤
        verbose_name = _('TemplateStep')
        verbose_name_plural = _('TemplateSteps')

class TemplateStepScript(models.Model):
    '''
    @note: 模板步骤-执行脚本
    '''
    step = models.ForeignKey(TemplateStep, verbose_name=_(u'模板步骤'))
    version = models.ForeignKey(Version, verbose_name=_(u'脚本版本'), blank=True, null=True)
    parameter = models.CharField(max_length=256, verbose_name=_(u'入口参数'), blank=True, null=True,default="")
    timeout = models.IntegerField(verbose_name=_(u'超时时间'), blank=True, null=True,default=0)
    audit_log = AuditLog()

    def __unicode__(self):
        return '%s %s'%(self.step.name, self.version.name)

    class Meta: #模板步骤-执行脚本
        verbose_name = _('TemplateStepScript')
        verbose_name_plural = _('TemplateStepScripts')


class TemplateFileInfo(models.Model):
    """
        分发,拉取文件的文件信息
    """
    step = models.ForeignKey(TemplateStep, verbose_name=_(u'模板步骤'))
    remote_ip = models.CharField(max_length=256, verbose_name=_(u'远程IP'), blank=True, null=True)
    push_account = models.ForeignKey(Account, verbose_name=_(u'远程机器常用账户'), blank=True, null=True)
    location_type = models.IntegerField(max_length=32,verbose_name=_(u'上传类型'),choices=enum_template.UPLOAD_TYPE_CHOICES,default=enum_template.UPLOAD_TYPE_LOCAL)
    remote_path = models.FilePathField(verbose_name=_(u'远程文件路径'),blank=True,null=True)
    record  = models.ForeignKey(UploadRecord, verbose_name=_(u'上传记录'),blank=True,null=True)
    audit_log = AuditLog()

class TemplateStepPushFile(models.Model):
    '''
    @note: 模板步骤-分发文件
    '''
    step = models.ForeignKey(TemplateStep, verbose_name=_(u'模板步骤'))
    limit = models.IntegerField(verbose_name=_(u'限速'),default=0)
    push_to = models.CharField(max_length=256, verbose_name=_(u'分发至'),default="")
    audit_log = AuditLog()
    
    def __unicode__(self):
        return '%s %s'%(self.step.name, self.push_to)

    class Meta: #模板步骤-分发文件
        verbose_name = _('TemplateStepPushFile')
        verbose_name_plural = _('TemplateStepPushFiles')

class TemplateStepPullFile(models.Model):
    '''
    @note: 模板步骤-拉取文件
    '''
    step = models.ForeignKey(TemplateStep, verbose_name=_(u'模板步骤'))
    limit = models.IntegerField(verbose_name=_(u'限速'),default=0)
    pull_to = models.CharField(max_length=256, verbose_name=_(u'拉取至'),default="")
    pull_to_ip = models.CharField(max_length=256, verbose_name=_(u'拉取至IP'),default="")
    file_paths = models.TextField(verbose_name=_(u'待拉取文件'), default=[])
    audit_log = AuditLog()
    
    def __unicode__(self):
        return '%s %s'%(self.step.name, self.pull_to)

    class Meta: #模板步骤-拉取文件
        verbose_name = _('TemplateStepPullFile')
        verbose_name_plural = _('TemplateStepPullFiles')
        
class TemplateStepText(models.Model):
    '''
    @note: 模板步骤-文本步骤
    '''
    step = models.ForeignKey(TemplateStep, verbose_name=_(u'模板步骤'))
    describe = models.CharField(max_length=256, verbose_name=_(u'文本描述'), default="")
    audit_log = AuditLog()
    
    def __unicode__(self):
        return '%s %s'%(self.step.name, self.describe)

    class Meta: #模板步骤-文本步骤
        verbose_name = _('TemplateStepText')
        verbose_name_plural = _('TemplateStepTexts')
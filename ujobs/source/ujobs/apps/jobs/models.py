#encoding:utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from enums import enum_template
from apps.accounts.models import Account
from apps.template.models import Template
from apps.script.models import Version
from audit_log.models.managers import AuditLog
from apps.template.models import TemplateStep
from django.contrib.auth.models import User
from apps.files.models import UploadRecord

'''
Created on 2015-5-14

@author: wx
'''

class Job(models.Model):
    '''
    @note: 作业
    '''
    template = models.ForeignKey(Template, verbose_name=_(u'模板'))
    name = models.CharField(max_length=128, verbose_name=_(u'作业名称'))
#     status = models.IntegerField(verbose_name=_(u'作业执行状态'), choices=enum_job.JOB_STATUS_CHOICES, default=enum_job.STATUS0)
    remarks = models.CharField(max_length=256, verbose_name=_(u'备注'), blank=True, null=True)
    create_user = models.ForeignKey(User, verbose_name=_(u'创建人'), related_name='job_create_user', blank=True, null=True)
#    create_user = models.CharField(max_length=256, verbose_name=_(u'创建人'), blank=True, null=True)
    update_user = models.ForeignKey(User, verbose_name=_(u'更新人'), related_name='job_update_user', blank=True, null=True)
#    update_user = models.CharField(max_length=256, verbose_name=_(u'更新人'), blank=True, null=True)
    created = models.DateTimeField(verbose_name=_(u"创建时间"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_(u"更新时间"), auto_now=True)
    mode = models.IntegerField(verbose_name=_(u'执行模式'), choices=enum_template.TEMPLATE_MODE_CHOICES, default=enum_template.TEMPLATE_MODE_AUTO)
    account = models.ForeignKey(Account, verbose_name=_(u'常用账户'), blank=True, null=True)
    target = models.TextField(verbose_name=_(u'目标机器'), blank=True, null=True)
    is_delete = models.BooleanField(verbose_name=_(u'是否删除'), default=False)
    is_sync = models.BooleanField(verbose_name=_(u'是否同步'), default=True)
    audit_log = AuditLog()

    def __unicode__(self):
        return self.name
    

    class Meta: #作业
        verbose_name = _('Job')
        verbose_name_plural = _('Jobs')

class JobStep(models.Model):
    '''
    @note: 作业步骤
    '''
    job = models.ForeignKey(Job, verbose_name=_(u'作业'))
    template_step = models.ForeignKey(TemplateStep, verbose_name=_(u'模板步骤'))
    name = models.CharField(max_length=128, verbose_name=_(u'步骤名称'), blank=True, null=True)
    describe = models.CharField(max_length=256, verbose_name=_(u'步骤描述'), blank=True, null=True,default="")
    step_type = models.IntegerField(verbose_name=_(u'步骤类型'), choices=enum_template.STEP_TYPE_CHOICES, blank=True, null=True)
    order = models.IntegerField(verbose_name=_(u'步骤顺序'), blank=True, null=True)
    is_setting = models.BooleanField(verbose_name=_(u'单独设定'), default=False)
    account = models.ForeignKey(Account, verbose_name=_(u'常用账户'), blank=True, null=True)
    target = models.TextField(verbose_name=_(u'目标机器'), blank=True, null=True)
    is_checked = models.BooleanField(verbose_name=_(u'是否勾选'), default=True)
    is_delete = models.BooleanField(verbose_name=_(u'是否删除'), default=False)
    audit_log = AuditLog()

    def __unicode__(self):
        return self.name

    class Meta: #作业步骤
        verbose_name = _('JobStep')
        verbose_name_plural = _('JobSteps')

class JobStepScript(models.Model):
    '''
    @note: 作业步骤-执行脚本
    '''
    step = models.ForeignKey(JobStep, verbose_name=_(u'作业步骤'))
    version = models.ForeignKey(Version, verbose_name=_(u'脚本版本'), blank=True, null=True)
    parameter = models.CharField(max_length=256, verbose_name=_(u'入口参数'), blank=True, null=True)
    timeout = models.IntegerField(verbose_name=_(u'超时时间'), blank=True, null=True)
    audit_log = AuditLog()

    def __unicode__(self):
        return '%s %s'%(self.step.name, self.version.name)

    class Meta: #作业步骤-执行脚本
        verbose_name = _('JobStepScript')
        verbose_name_plural = _('JobStepScripts')

class JobFileInfo(models.Model):
    """
        每个步骤的文件记录
    """
    step = models.ForeignKey(JobStep, verbose_name=_(u'作业步骤'))
    remote_ip = models.CharField(max_length=256, verbose_name=_(u'远程IP'), blank=True, null=True)
    push_account = models.ForeignKey(Account, verbose_name=_(u'远程机器常用账户'), blank=True, null=True)
    location_type = models.IntegerField(max_length=32,verbose_name=_(u'上传类型'),choices=enum_template.UPLOAD_TYPE_CHOICES,default=enum_template.UPLOAD_TYPE_LOCAL)
    remote_path = models.FilePathField(verbose_name=_(u'远程文件路径'),blank=True,null=True)
    record  = models.ForeignKey(UploadRecord, verbose_name=_(u'上传记录'),blank=True,null=True)
    audit_log = AuditLog()

class JobStepPushFile(models.Model):
    '''
    @note: 作业步骤-分发文件
    '''
    step = models.ForeignKey(JobStep, verbose_name=_(u'作业步骤'))
    limit = models.IntegerField(verbose_name=_(u'限速'),default=0)
    push_to = models.CharField(max_length=256, verbose_name=_(u'分发至'),default="")
    audit_log = AuditLog()

    def __unicode__(self):
        return '%s %s'%(self.step.name, self.push_to)

    class Meta: #作业步骤-分发文件
        verbose_name = _('JobStepPushFile')
        verbose_name_plural = _('JobStepPushFiles')
        
class JobStepPullFile(models.Model):
    '''
    @note: 作业步骤-拉取文件
    '''
    step = models.ForeignKey(JobStep, verbose_name=_(u'作业步骤'))
    limit = models.IntegerField(verbose_name=_(u'限速'),default=0)
    pull_to = models.CharField(max_length=256, verbose_name=_(u'拉取至'),default="")
    pull_to_ip = models.CharField(max_length=256, verbose_name=_(u'拉取至IP'),default="")
    file_paths = models.TextField(verbose_name=_(u'待拉取文件'), default=[])
    audit_log = AuditLog()

    def __unicode__(self):
        return '%s %s'%(self.step.name, self.pull_to)

    class Meta: #作业步骤-拉取文件
        verbose_name = _('JobStepPullFile')
        verbose_name_plural = _('JobStepPullFiles')
        
class JobStepText(models.Model):
    '''
    @note: 作业步骤-文本步骤
    '''
    step = models.ForeignKey(JobStep, verbose_name=_(u'作业步骤'))
    describe = models.CharField(max_length=256, verbose_name=_(u'文本描述'), default="")
    audit_log = AuditLog()

    def __unicode__(self):
        return '%s %s'%(self.step.name, self.describe)

    class Meta: #作业步骤-文本步骤
        verbose_name = _('JobStepText')
        verbose_name_plural = _('JobStepTexts')


class APScheduleJobs(models.Model):
    '''
        @note: apshedule table.
    '''
    id = models.CharField(max_length=255, verbose_name=_(u'ID'), default="",primary_key=True)
    next_run_time = models.FloatField(verbose_name=_(u'下次执行时间'), default="")
    job_state = models.BinaryField(verbose_name=_(u'作业内容'))

    def __unicode__(self):
        return '%s %s'%(self.id,self.next_run_time)

    class Meta:
        verbose_name = _('APScheduleJobs')
        verbose_name_plural = _('APScheduleJobs')
        db_table = "apscheduler_jobs"

class ScheduleJobs(models.Model):
    '''
        @note: schedule jobs.
    '''
    job = models.ForeignKey(Job, verbose_name=_(u'作业'))
    creator = models.ForeignKey(User, verbose_name=_(u'创建人'),blank=True, null=True,related_name="schedule_creator")
    executor = models.ForeignKey(User, verbose_name=_(u'启动人'),blank=True, null=True,related_name="schedule_executor")
    # schedule = models.ForeignKey(APScheduleJobs, verbose_name=_(u'计划任务'),blank=True, null=True)
    schedule_id = models.CharField(max_length=255, verbose_name=_(u'后台定时任务id'), default="")
    expression = models.CharField(max_length=255, verbose_name=_(u'定时表达式'), default="")
    status = models.IntegerField(max_length=32,verbose_name=_(u'当前状态'),choices=enum_template.SCHEDULE_STATUS_CHOICES,default=enum_template.SCHEDULE_STATUS_STARTED)
    created = models.DateTimeField(verbose_name=_(u"创建时间"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_(u"更新时间"), auto_now=True)
    note = models.TextField(verbose_name=_(u'任务描述'), blank=True, null=True,default="")
    audit_log = AuditLog()

    def __unicode__(self):
        return '%s %s'%(self.id,self.expression)

    class Meta:
        verbose_name = _('APScheduleJobs')
        verbose_name_plural = _('APScheduleJobs')

from settings import scheduler
if not scheduler.running:
    scheduler.start()
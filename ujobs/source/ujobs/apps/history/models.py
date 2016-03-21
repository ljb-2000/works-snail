#encoding:utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from enums import enum_history, enum_template
from apps.accounts.models import Account
from apps.jobs.models import Job, JobStep, ScheduleJobs
from apps.script.models import Version
from apps.files.models import UploadRecord
from django.contrib.auth.models import User

'''
Created on 2015-5-18

@author: wx
'''

class History(models.Model):
    '''
    @note: 作业历史
    '''
    job = models.ForeignKey(Job, verbose_name=_(u'作业'))
    name = models.CharField(max_length=128, verbose_name=_(u'作业名称'))
    remarks = models.CharField(max_length=256, verbose_name=_(u'备注'), blank=True, null=True)
    mode = models.IntegerField(verbose_name=_(u'执行模式'), choices=enum_template.TEMPLATE_MODE_CHOICES, default=enum_template.TEMPLATE_MODE_AUTO)
    account = models.ForeignKey(Account, verbose_name=_(u'常用账户'), blank=True, null=True)
    target = models.TextField(verbose_name=_(u'目标机器'), blank=True, null=True)
    start_time = models.DateTimeField(verbose_name=_(u"开始时间"), blank=True, null=True)
    end_time = models.DateTimeField(verbose_name=_(u"结束时间"), blank=True, null=True)
    delta_time = models.IntegerField(verbose_name=_(u'总耗时'), blank=True, null=True)
    user = models.ForeignKey(User, verbose_name=_(u'执行人'), related_name='history_create_user', blank=True, null=True)
    status = models.IntegerField(verbose_name=_(u'作业执行状态'), choices=enum_history.HISTORY_STATUS_CHOICES, default=enum_history.STATUS_NOT_START)
    startup_type = models.IntegerField(verbose_name=_(u'作业启动方式'), choices=enum_history.HISTORY_RUN_TYPE_CHOICES, default=enum_history.HISTORY_STARTUP_TYPE_MANUAL)
#    def __unicode__(self):
#        return self.name

    class Meta: #作业历史
        verbose_name = _('History')
        verbose_name_plural = _('Historys')
        
class HistoryStep(models.Model):
    '''
    @note: 步骤历史
    '''
    history = models.ForeignKey(History, verbose_name=_(u'作业历史'))
    jobstep = models.ForeignKey(JobStep, verbose_name=_(u'作业步骤'))
    name = models.CharField(max_length=128, verbose_name=_(u'步骤名称'), blank=True, null=True)
    describe = models.CharField(max_length=256, verbose_name=_(u'步骤描述'), blank=True, null=True,default="")
    order = models.IntegerField(verbose_name=_(u'步骤顺序'), blank=True, null=True)
    is_setting = models.BooleanField(verbose_name=_(u'单独设定'), default=False)
    account = models.ForeignKey(Account, verbose_name=_(u'常用账户'), blank=True, null=True)
    target = models.TextField(verbose_name=_(u'目标机器'), blank=True, null=True)
    start_time = models.DateTimeField(verbose_name=_(u"开始时间"), blank=True, null=True)
    end_time = models.DateTimeField(verbose_name=_(u"结束时间"), blank=True, null=True)
    delta_time = models.IntegerField(verbose_name=_(u'步骤耗时'), blank=True, null=True)
    result = models.IntegerField(verbose_name=_(u'步骤执行结果'), choices=enum_history.HISTORYSTEP_RESULT_CHOICES, default=enum_history.RESULT_NOT_START)
    total_ips = models.TextField(verbose_name=_(u'目标IP'), blank=True, null=True,default=[])
    abnormal_ips = models.TextField(verbose_name=_(u'检测失败IP'), blank=True, null=True,default=[])
    fail_ips = models.TextField(verbose_name=_(u'执行失败IP'), blank=True, null=True,default=[])
    success_ips = models.TextField(verbose_name=_(u'执行成功IP'), blank=True, null=True,default=[])
    
#    def __unicode__(self):
#        return self.name

    class Meta: #步骤历史
        verbose_name = _('HistoryStep')
        verbose_name_plural = _('HistorySteps')

class HistoryStepScript(models.Model):
    '''
    @note: 步骤历史-执行脚本
    '''
    step = models.ForeignKey(HistoryStep, verbose_name=_(u'步骤历史'))
    version = models.ForeignKey(Version, verbose_name=_(u'脚本版本'))
    parameter = models.CharField(max_length=256, verbose_name=_(u'入口参数'), blank=True, null=True)
    timeout = models.IntegerField(verbose_name=_(u'超时时间'), blank=True, null=True)
        
    def __unicode__(self):
        return '%s %s'%(self.step.name, self.version.name)

    class Meta: #步骤历史-执行脚本
        verbose_name = _('HistoryStepScript')
        verbose_name_plural = _('HistoryStepScripts')

class HistoryFileInfo(models.Model):
    """
        每个步骤的文件记录
    """
    step = models.ForeignKey(HistoryStep, verbose_name=_(u'作业步骤'))
    remote_ip = models.CharField(max_length=256, verbose_name=_(u'远程IP'), blank=True, null=True)
    push_account = models.ForeignKey(Account, verbose_name=_(u'远程机器常用账户'), blank=True, null=True)
    location_type = models.IntegerField(max_length=32,verbose_name=_(u'上传类型'),choices=enum_template.UPLOAD_TYPE_CHOICES,default=enum_template.UPLOAD_TYPE_LOCAL)
    remote_path = models.FilePathField(verbose_name=_(u'远程文件路径'),blank=True,null=True)
    record  = models.ForeignKey(UploadRecord, verbose_name=_(u'上传记录'),blank=True,null=True)

class HistoryStepPushFile(models.Model):
    '''
    @note: 步骤历史-分发文件
    '''
    step = models.ForeignKey(HistoryStep, verbose_name=_(u'步骤历史'))
    limit = models.IntegerField(verbose_name=_(u'限速'))
    push_to = models.CharField(max_length=256, verbose_name=_(u'分发至'))
            
    def __unicode__(self):
        return '%s %s'%(self.step.name, self.push_to)

    class Meta: #步骤历史-分发文件
        verbose_name = _('HistoryStepPushFile')
        verbose_name_plural = _('HistoryStepPushFiles')
        
class HistoryStepPullFile(models.Model):
    '''
    @note: 步骤历史-拉取文件
    '''
    step = models.ForeignKey(HistoryStep, verbose_name=_(u'步骤历史'))
    limit = models.IntegerField(verbose_name=_(u'限速'),default=0)
    pull_to = models.CharField(max_length=256, verbose_name=_(u'拉取至'),default="")
    pull_to_ip = models.CharField(max_length=256, verbose_name=_(u'拉取至IP'),default="")
    file_paths = models.TextField(verbose_name=_(u'待拉取文件'), default=[])
            
    def __unicode__(self):
        return '%s %s'%(self.step.name, self.pull_to)

    class Meta: #步骤历史-拉取文件
        verbose_name = _('HistoryStepPullFile')
        verbose_name_plural = _('HistoryStepPullFiles')
        
class HistoryStepText(models.Model):
    '''
    @note: 步骤历史-文本步骤
    '''
    step = models.ForeignKey(HistoryStep, verbose_name=_(u'步骤历史'))
    describe = models.CharField(max_length=256, verbose_name=_(u'文本描述'), blank=True, null=True)
        
    def __unicode__(self):
        return '%s %s'%(self.step.name, self.describe)

    class Meta: #步骤历史-文本步骤
        verbose_name = _('HistoryStepText')
        verbose_name_plural = _('HistoryStepTexts')

class RunningResult(models.Model):
    """
        每个步骤的IP操作列表
    """
    step = models.ForeignKey(HistoryStep, verbose_name=_(u'历史作业步骤'))
    ip = models.CharField(max_length=64,verbose_name=_(u"目标机器IP"), blank=True, null=True,default='*',db_index=True) # use * for all ip
    res_time = models.DateTimeField(verbose_name=_(u"记录时间"), blank=True, null=True,auto_now=True)
    content = models.TextField(verbose_name=_(u"操作内容"), blank=True, null=True)
    progress = models.PositiveIntegerField(verbose_name=_(u'进度'), blank=True, null=True, default=0,db_index=True)


class ScheduleHistory(models.Model):
    """
        自动执行历史
    """
    task = models.ForeignKey(ScheduleJobs, verbose_name=_(u'执行任务'))
    history = models.ForeignKey(History, verbose_name=_(u'执行历史'),blank=True, null=True)
    result = models.IntegerField(max_length=32,verbose_name=_(u'启动结果'),choices=enum_history.SCHEDULE_HISTORY_RESULT_CHOICES,default=enum_history.SCHEDULE_HISTORY_RESULT_FAIL)
    info = models.TextField(verbose_name=_(u"启动信息"), blank=True, null=True,default="")
    trigger_time = models.DateTimeField(verbose_name=_(u"触发时间"), blank=True, null=True,auto_now=True)

    def __unicode__(self):
        return '%s %s'%(self.task.job.name, self.id)

    class Meta:
        verbose_name = _('ScheduleHistory')
        verbose_name_plural = _('ScheduleHistory')
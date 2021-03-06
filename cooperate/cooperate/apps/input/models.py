#encoding:utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from audit_log.models.managers import AuditLog

        
class FileUpload(models.Model):
    '''
    @note: 文档管理
    '''
    user = models.ForeignKey(User, verbose_name=_(u'用户'))
    file_name = models.CharField(max_length=128,verbose_name=_(u'上传文件名'), blank=True, null=True)
    file_path = models.CharField(max_length=128,verbose_name=_(u'上传地址'), blank=True, null=True)
    upload_time = models.DateTimeField(verbose_name=_(u"上传时间"), blank=True, null=True)

    def __unicode__(self):
        return '%s:%s'%(self.user.username,self.file_name)
    

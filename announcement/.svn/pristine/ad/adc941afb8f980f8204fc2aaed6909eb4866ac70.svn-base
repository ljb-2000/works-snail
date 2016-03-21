#encoding:utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from audit_log.models.managers import AuditLog

class Product(models.Model):
    '''
    @note: 业务
    '''
    name = models.CharField(max_length=128, verbose_name=_(u'业务名称'), unique=True)
    file_name = models.CharField(max_length=128, verbose_name=_(u'公告文件名'))
    ftp_host = models.CharField(max_length=128, verbose_name=_(u'FTP主机'), blank=True, null=True)
    ftp_port = models.CharField(max_length=128, verbose_name=_(u'FTP端口'), blank=True, null=True)
    ftp_username = models.CharField(max_length=128, verbose_name=_(u'FTP登录名'), blank=True, null=True)
    ftp_password = models.CharField(max_length=128, verbose_name=_(u'FTP密码'), blank=True, null=True)
    create_user = models.ForeignKey(User, verbose_name=_(u'创建人'), related_name='product_create_user', blank=True, null=True)
    update_user = models.ForeignKey(User, verbose_name=_(u'更新人'), related_name='product_update_user', blank=True, null=True)
    updated = models.DateTimeField(verbose_name=_(u"更新时间"), auto_now=True)
    audit_log = AuditLog()

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')      
        
class ProductInfo(models.Model):
    '''
    @note: 业务
    '''
    product = models.ForeignKey(Product, verbose_name=_(u'业务'))
    group_name = models.CharField(max_length=128,verbose_name=_(u'公告分组名称'), blank=True, null=True)
    group_path = models.CharField(max_length=128,verbose_name=_(u'公告分组路径'), blank=True, null=True)
    create_user = models.ForeignKey(User, verbose_name=_(u'创建人'), related_name='productInfo_create_user', blank=True, null=True)
    update_user = models.ForeignKey(User, verbose_name=_(u'更新人'), related_name='productInfo_update_user', blank=True, null=True)
    created = models.DateTimeField(verbose_name=_(u"创建时间"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_(u"更新时间"), auto_now=True)
    audit_log = AuditLog()

    def __unicode__(self):
        return '%s-%s'%(self.product.name,self.group_name)
    
    class Meta:
        verbose_name = _('ProductInfo')
        verbose_name_plural = _('ProductInfos')
        
class FileUploadLog(models.Model):
    '''
    @note: 文件上传记录
    '''
    user = models.ForeignKey(User, verbose_name=_(u'用户'))
    file_name = models.CharField(max_length=128,verbose_name=_(u'上传文件名'), blank=True, null=True)
    file_path = models.CharField(max_length=128,verbose_name=_(u'上传文件路径'), blank=True, null=True)
    log = models.CharField(max_length=128,verbose_name=_(u'上传结果记录'), blank=True, null=True)
    start_time = models.DateTimeField(verbose_name=_(u"开始时间"), auto_now_add=True)
    end_time = models.DateTimeField(verbose_name=_(u"结束时间"), blank=True, null=True)

    def __unicode__(self):
        return '%s:%s-%s'%(self.user.username,self.file_name,self.file_path)
    
class FtpUploadLog(models.Model):
    '''
    @note: FTP上传记录
    '''
    user = models.ForeignKey(User, verbose_name=_(u'用户'))
    file_path = models.CharField(max_length=128,verbose_name=_(u'上传文件路径'), blank=True, null=True)
    ftp_path = models.CharField(max_length=128,verbose_name=_(u'上传ftp路径'), blank=True, null=True)
    log = models.CharField(max_length=128,verbose_name=_(u'上传结果记录'), blank=True, null=True)
    start_time = models.DateTimeField(verbose_name=_(u"开始时间"), auto_now_add=True)
    end_time = models.DateTimeField(verbose_name=_(u"结束时间"), blank=True, null=True)

    def __unicode__(self):
        return '%s:%s-%s'%(self.user.username,self.file_path,self.ftp_path)
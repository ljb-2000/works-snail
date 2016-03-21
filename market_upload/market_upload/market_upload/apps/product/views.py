#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

import settings
from utils.decorator import render_to, login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.transaction import commit_on_success
from django.shortcuts import HttpResponse
import json
import datetime
from ftplib import FTP
import logging
import traceback
from releaseinfo import bufsize, SPECIAL_USERS, PRODUCT_URL, FTP_HOST, FTP_PORT, FTP_USERNAME, FTP_PASSWORD, FTP_DOMAIN
from service import _product
import hashlib, base64
import urllib, urllib2
from pypinyin import lazy_pinyin, load_phrases_dict
import threading

logger = logging.getLogger('logger')

load_phrases_dict({u'音乐侠': [[u'yin'], [u'yue'], [u'xia']]})
load_phrases_dict({u'横行冒险王': [[u'heng'], [u'xing'], [u'mao'], [u'xian'], [u'wang']]})

@csrf_exempt
@login_required
def save(request):
    user = request.user
    sdicts = {}
    sdicts["result"] = 0
    product_name = request.POST.get('product_name','').strip()
    ftp_info = request.POST.get('ftp_info','').strip()
    ftp_domain = request.POST.get('ftp_domain','').strip()
    file_path = request.POST.get('file_path','').strip()
    
    if ftp_info:
        try:
            ftp_info_list = ftp_info.split(',')
            ftp_host = ftp_info_list[0].strip()
            ftp_port = ftp_info_list[1].strip()
            ftp_username = ftp_info_list[2].strip()
            ftp_password = ftp_info_list[3].strip()
        except:
            sdicts["msg"] = u'资源ftp站点信息有误！'
            return HttpResponse(json.dumps(sdicts, ensure_ascii=False))
    else:
        ftp_host = FTP_HOST
        ftp_port = FTP_PORT
        ftp_username = FTP_USERNAME
        ftp_password = FTP_PASSWORD
    
    if not ftp_domain:
        ftp_domain = FTP_DOMAIN
    
    if not file_path:
        product_pinyin_list = lazy_pinyin(product_name, errors='ignore')
        file_path = ''.join(product_pinyin_list)
    
    ftp_domain = ftp_domain.replace('\\','/').strip('/')
    file_path = file_path.replace('\\','/').strip('/')
    
    #验证路径是否存在
    product = _product.get_product_by_params(name=product_name)
    if product:
        product_list = _product.get_products_by_params().exclude(id=product.id)
    else:
        product_list = _product.get_products_by_params()
    for product_exist in product_list:
        if file_path == product_exist.file_path:
            sdicts["msg"] = u'业务路径已存在'
            return HttpResponse(json.dumps(sdicts, ensure_ascii=False))
    
    product = _product.get_or_create_product_by_params(name=product_name)[0]
    product.ftp_host = ftp_host
    product.ftp_port = ftp_port
    product.ftp_username = base64.b64encode(ftp_username)
    product.ftp_password = base64.b64encode(ftp_password)
    product.ftp_domain = ftp_domain
    product.file_path = file_path
    product.create_user = user
    product.update_user = user
    product.save()
    
    sdicts["result"] = 1
    sdicts["msg"] = u'保存业务信息成功'
    return HttpResponse(json.dumps(sdicts, ensure_ascii=False))

@csrf_exempt
def file_upload(request):
    user = request.user
    result_dict = {'result':0}
    sfile = request.FILES.get("Filedata",None)
    product_id = request.POST.get("product_id",0)
    if sfile and product_id:
        ftpUploadLogs = _product.get_ftpUploadLogs_by_params().order_by('-id')
        if ftpUploadLogs:
            info_num = ftpUploadLogs[0].id
        else:
            info_num = 0
        
        product = _product.get_product_by_params(id=product_id)
        file_name = sfile.name
        result_dict = web_upload(sfile,file_name)
        
        ftp_domain = product.ftp_domain
        remotepath = product.file_path
        host = product.ftp_host
        port = int(product.ftp_port)
        
        ftpUploadLog = _product.create_ftpUploadLog_by_params(user=user, product=product)
        ftpUploadLog.ftp_host = host
        ftpUploadLog.ftp_port = port
        ftpUploadLog.ftp_domain = ftp_domain
        ftpUploadLog.ftp_path = remotepath
        ftpUploadLog.file_name = file_name
        ftpUploadLog.save()
        
        thread = threading.Thread(target=ftp_upload,args=(user,product,file_name,ftpUploadLog))
#         thread_name = 'Thread-history-%s'%history.id
#         thread.setName(thread_name)
        thread.start()
        
        result_dict['info_id'] = info_num + 1
#         result_dict =ftp_upload(user,product,sfile,file_name)

    return HttpResponse(json.dumps(result_dict), content_type="application/json")

def web_upload(sfile,file_name):
    '''文件上传ftp'''
    sdicts = {}
    sdicts["result"] = 0
    sdicts["file_url"] = FTP_DOMAIN + file_name
    try:
        file_path=os.path.join(settings.MEDIA_ROOT, file_name)
        fp = open(file_path, 'wb')
        for content in sfile.chunks(): 
            fp.write(content)
        fp.close()
        sdicts["result"] = 1
    except Exception,e:
        print e
    return sdicts

@csrf_exempt
def ftp_upload(user,product,file_name,ftpUploadLog):
    username = base64.b64decode(product.ftp_username)
    password = base64.b64decode(product.ftp_password)
    remotepath = product.file_path
    host = product.ftp_host
    port = int(product.ftp_port)
    
    ftp=FTP()
    ftp.set_debuglevel(2)#打开调试级别2，显示详细信息;0为关闭调试信息 
    logger.debug("ftp login start")
    
    try:
        ftp.connect(host, port)
        logger.debug("ftp connect success")
    except Exception,e:
        print e
        ftpUploadLog.log = 'error--ftp connection fail:%s'%e
        ftpUploadLog.end_time = datetime.datetime.now()
        ftpUploadLog.save()
    
    try:
        ftp.login(username, password)
        logger.debug("ftp login success")
    except Exception,e:
        print e
        ftpUploadLog.log = 'error--ftp login fail:%s'%e
        ftpUploadLog.end_time = datetime.datetime.now()
        ftpUploadLog.save()
    
    remotepath_list = remotepath.split('/')
    for remotedir in remotepath_list:
        try:
            ftp.cwd(remotedir)
        except:
            ftp.mkd(remotedir)
            ftp.cwd(remotedir)
    logger.debug("ftp change dir success")
    
    try:
        file_path=os.path.join(settings.MEDIA_ROOT, file_name)
        fp = open(file_path, 'rb')
        ftp.storbinary('STOR %s' % file_name,fp,bufsize)
        fp.close()
    except Exception,e:
        print e
        fp.close()
        ftpUploadLog.log = 'error--ftp stor file fail:%s'%e
        ftpUploadLog.end_time = datetime.datetime.now()
        ftpUploadLog.save()
    
    ftp.set_debuglevel(0)
    ftp.quit()
    
    logger.debug("file upload success")
    ftpUploadLog.log = 'file upload success'
    ftpUploadLog.end_time = datetime.datetime.now()
    ftpUploadLog.save()
    
# @csrf_exempt
# def ftp_upload(user,product,sfile,file_name):
#     sdicts = {}
#     sdicts["result"] = 0
#     
#     host = product.ftp_host
#     port = int(product.ftp_port)
#     username = base64.b64decode(product.ftp_username)
#     password = base64.b64decode(product.ftp_password)
#     
#     ftp_domain = product.ftp_domain
#     remotepath = product.file_path
#     file_url = os.path.join(ftp_domain,remotepath,file_name)
#     sdicts["file_url"] = file_url.replace('\\','/')
#     
#     ftpUploadLog = _product.create_ftpUploadLog_by_params(user=user, product=product)
#     ftpUploadLog.ftp_host = host
#     ftpUploadLog.ftp_port = port
#     ftpUploadLog.ftp_domain = ftp_domain
#     ftpUploadLog.ftp_path = remotepath
#     ftpUploadLog.file_name = file_name
#     
#     ftp=FTP()
#     ftp.set_debuglevel(2)#打开调试级别2，显示详细信息;0为关闭调试信息 
#     logger.debug("ftp login start")
#     
#     try:
#         ftp.connect(host, port)
#         logger.debug("ftp connect success")
#     except Exception,e:
#         print e
#         sdicts["msg"] = u"文件上传失败！"
#         ftpUploadLog.log = 'ftp connection fail:%s'%e
#         ftpUploadLog.end_time = datetime.datetime.now()
#         ftpUploadLog.save()
#         return HttpResponse(json.dumps(sdicts, ensure_ascii=False))
#     
#     try:
#         ftp.login(username, password)
#         logger.debug("ftp login success")
#     except Exception,e:
#         print e
#         sdicts["msg"] = u"文件上传失败！"
#         ftpUploadLog.log = 'ftp login fail:%s'%e
#         ftpUploadLog.end_time = datetime.datetime.now()
#         ftpUploadLog.save()
#         return HttpResponse(json.dumps(sdicts, ensure_ascii=False))
#     
#     remotepath_list = remotepath.split('/')
#     for remotedir in remotepath_list:
#         try:
#             ftp.cwd(remotedir)
#         except:
#             ftp.mkd(remotedir)
#             ftp.cwd(remotedir)
#     logger.debug("ftp change dir success")
#     
#     try:    
#         ftp.storbinary('STOR %s' % file_name,sfile,bufsize)
#     except Exception,e:
#         print e
#         sdicts["msg"] = u"文件上传失败！"
#         ftpUploadLog.log = 'ftp stor file fail:%s'%e
#         ftpUploadLog.end_time = datetime.datetime.now()
#         ftpUploadLog.save()
#         return HttpResponse(json.dumps(sdicts, ensure_ascii=False))
#     
#     ftp.set_debuglevel(0)
#     ftp.quit()
#     
#     ftpUploadLog.log = 'file upload success'
#     ftpUploadLog.end_time = datetime.datetime.now()
#     ftpUploadLog.save()
#     
#     sdicts['result'] = 1 
#     sdicts["msg"] = u"文件上传成功！"
#     
#     return sdicts
    
@csrf_exempt
def download_file(request):   
    # Text file
    now = datetime.datetime.now()         
    text = request.GET.get('text','')
    text_list = text.split(',')
    response = HttpResponse()
    response['ContentType'] = 'text/plain'
    response['Content-Disposition'] = 'attachment; filename=links_%s.txt'%datetime.datetime.strftime(now,'%Y%m%d%H%M%S')
    response.write('\r\n'.join(text_list))  
              
    return response

@csrf_exempt
def ajax_get_product_option(request):
    user = request.user
    
    products_add = []
    try:
        if user.username in SPECIAL_USERS:
            name = u'张延礼'
        data = {'username':name.encode('utf8'),}
        
        req = urllib2.Request(PRODUCT_URL)
        params = urllib.urlencode(data)
        response = urllib2.urlopen(req, params)
        
        jsonText = response.read()
        json_dict= json.loads(jsonText)
        
        product_dict_list = json_dict.get('items')
        for product_dict in product_dict_list:
            products_name = product_dict.get('VERSION_NAME')
            products_add.append(products_name)
    except Exception,e:
        print e
    
    products = _product.get_products_by_params(name__in=products_add)
    res = []
    for product in products:
        obj = [product.id, product.name]
        res.append(obj)
    result = json.dumps(res)
    return HttpResponse(result)
    
@csrf_exempt
def ajax_get_productinfo(request):
    sdicts = {}
    sdicts['result'] = 0
    if request.method == "POST":
        product_name = request.POST.get('product_name',0)
        product_pinyin_list = lazy_pinyin(product_name, errors='ignore')
        file_path_default = ''.join(product_pinyin_list)
        sdicts['file_path_default'] = file_path_default
        
        product = _product.get_product_by_params(name=product_name)
        if product:
            sdicts['ftp_host'] = product.ftp_host
            sdicts['ftp_port'] = product.ftp_port
            sdicts['ftp_username'] = base64.b64decode(product.ftp_username)
            sdicts['ftp_password'] = base64.b64decode(product.ftp_password)
            sdicts['ftp_domain'] = product.ftp_domain
            sdicts['file_path'] = product.file_path
            sdicts['result'] = 1
    return HttpResponse(json.dumps(sdicts))

def calc_md5(filepath):
    with open(filepath,'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        hash_value = md5obj.hexdigest()
        return hash_value
    
@csrf_exempt
def ajax_get_upload_info(request):
    sdicts = {} 
    sdicts['result'] = 0
    if request.method == "POST":
        product_id = request.POST.get("product_id",0)
        info_id = request.POST.get('info_id',0)
        fsize = int(request.POST.get('size',0))
        file_name = request.POST.get('name')
        
        info = _product.get_ftpUploadLog_by_params(id=info_id)
        
        if product_id and info:
            if info.log:
                if 'success' in info.log:
                    file_url = os.path.join(info.ftp_domain,info.ftp_path,info.file_name)
                    file_url = file_url.replace('\\','/')
                    sdicts['file_url'] = file_url
                    sdicts['percent'] = 100
                    sdicts['result'] = 1
            else:
                product = _product.get_product_by_params(id=product_id)
                username = base64.b64decode(product.ftp_username)
                password = base64.b64decode(product.ftp_password)
                remotepath = product.file_path
                host = product.ftp_host
                port = int(product.ftp_port)
                
                ftp=FTP()
                ftp.set_debuglevel(2)#打开调试级别2，显示详细信息;0为关闭调试信息 
                
                try:
                    ftp.connect(host, port)
                    ftp.login(username, password)
                
                    remotepath_list = remotepath.split('/')
                    for remotedir in remotepath_list:
                        ftp.cwd(remotedir)
                    rsize = ftp.size(file_name)
                    sdicts['percent'] = '%.f'%(rsize*1.0 / fsize * 100)
                except Exception,e:
                    sdicts['percent'] = 0
                    print e
                
                ftp.set_debuglevel(0)
                ftp.quit()
                sdicts['result'] = 1
                
    return HttpResponse(json.dumps(sdicts))
# -- encoding=utf-8 --
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

import settings

from django.db.models import Q
from utils.decorator import render_to, login_required
from django.db.transaction import commit_on_success
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import logging
import traceback
import json
import datetime
from apps.input.models import FileUpload
from service import _input, _report
from releaseinfo import REL_MEDIA_URL, QUESTION_API, SPECIAL_USERS, SPECIAL_USER_NAME
import requests
from utils.util import get_product_list_by_user

logger = logging.getLogger("logger")

@login_required
@csrf_exempt
@render_to('input/upload.html')
def upload_index(request):
    return locals()

@csrf_exempt
def ajax_get_files(request):
    file_list = []
    
    textstr = request.POST.get('textstr')
    length = request.POST.get('length', 10)
    if textstr:
        fileuploads = FileUpload.objects.filter(Q(file_name__icontains=textstr)|Q(user__username__icontains=textstr)).order_by('-id')
    else:
        fileuploads = _input.get_fileUploads_by_params().order_by('-id')
    if length:
        fileuploads = fileuploads[:int(length)]
    for file in fileuploads:
        id = file.id
        name = file.file_name
        user = file.user.username
        time = datetime.datetime.strftime(file.upload_time,'%Y-%m-%d %H:%M')
        download = u'%s%s/%s/%s'%(REL_MEDIA_URL, user, datetime.datetime.strftime(file.upload_time,'%Y%m%d%H%M%S'), name)
        delete = False
        if file.user == request.user:
            delete = True
        file_list.append({'id':id, 'name':name, 'user': user, 'time': time, 'download':download, 'del':delete})
        
    return HttpResponse(json.dumps(file_list), content_type="application/json")

@csrf_exempt
@commit_on_success
def ajax_upload_file(request):
    user = request.user
    sdicts = {'result':0}
    sfile = request.FILES.get("upload_file",None)
    if sfile:
        file_name = u'%s'%sfile.name
        try:
            now = datetime.datetime.now()
            file_path=os.path.join(settings.MEDIA_ROOT, user.username)
            if not os.path.exists(file_path):
                os.mkdir(file_path)
            file_path=os.path.join(file_path, file_name)
            
            fp = open(file_path, 'wb')
            for content in sfile.chunks(): 
                fp.write(content)
            fp.close()
            
            file_upload = _input.get_or_create_fileUpload_by_params(user=user,file_name=file_name)[0]
            file_upload.file_path=os.path.join(user.username, file_name)
            file_upload.upload_time=now
            file_upload.save()
            
            sdicts["result"] = 1
        except Exception,e:
            print e
    return HttpResponse(json.dumps(sdicts), content_type="application/json")

@csrf_exempt
@commit_on_success
def ajax_delete_file(request):
    sdicts = {'result':0}
    
    file_id = request.POST.get('id')
    
    if file_id:
        try:
            file_upload = _input.get_fileUpload_by_params(id=int(file_id))
            file_path = os.path.join(settings.MEDIA_ROOT, file_upload.file_path)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                
            file_upload.delete()
            sdicts["result"] = 1
        except Exception,e:
            print e
    return HttpResponse(json.dumps(sdicts), content_type="application/json")

@login_required
@csrf_exempt
@render_to('input/issue.html')
def issue_index(request):
    user = request.user
    cnname = user.first_name
    if user.username in SPECIAL_USERS:
        cnname = SPECIAL_USER_NAME
    product_names = get_product_list_by_user(cnname)
    products = _report.get_products_by_params(name__in=product_names)
    return locals()

@csrf_exempt
def ajax_add_issue(request):
    result = {"result": 0}
    
    try:
        product_name = request.POST.get('product_name','').strip()
        qtime = request.POST.get('qtime','').strip()
        status = request.POST.get('status')
        level = request.POST.get('level')
        qtype = request.POST.get('qtype')
        title = request.POST.get('title','').strip()
        describe = request.POST.get('describe','').strip()
        reason = request.POST.get('reason','').strip()
        solution = request.POST.get('solution','').strip()
    
        data = {
                'username' : request.user.username,
                'product_name' : product_name,
                'qtime' : qtime,
                'status' : status,
                'level' : level,
                'qtype' : qtype,
                'title' : title,
                'describe' : describe,
                'reason' : reason,
                'solution' : solution,
                }
        r = requests.post(QUESTION_API, data=data)
        result =  json.loads(r.text)
    except Exception,e:
        print e
    return HttpResponse(json.dumps(result), content_type="application/json")

from django.conf.urls import patterns, url
urlpatterns = patterns('',
    url(r'^input/upload/$', upload_index, name='upload_index'),
    url(r'^input/ajax_get_files/$', ajax_get_files, name='ajax_get_files'),
    url(r'^input/ajax_upload_file/$', ajax_upload_file, name='ajax_upload_file'),
    url(r'^input/ajax_delete_file/$', ajax_delete_file, name='ajax_delete_file'),

    url(r'^input/issue/$', issue_index, name='issue_index'),
    url(r'^input/ajax_add_issue/$', ajax_add_issue, name='ajax_add_issue'),
    
)
# -- encoding=utf-8 --
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from utils.decorator import render_to, login_required
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from django.core.paginator import Paginator
from service import _job
import datetime
from utils.ctranslate import LazyEncoder
from enums.enum_template import USER_TEMPLATE_TYPES
from enums.enum_account import PERM_PTYPE_JOB
from django.db.models import Q
from apps.accounts.models import Perm

@login_required
@csrf_exempt
@render_to('example_manage/contentDiv.html')
def example_manage_index(request):
    table_fields = [u'作业实例名称', u'所属作业模板名称', u'备注', u'创建人', u'创建时间', u'最后修改人', u'最后修改时间']
    ajax_url = u'/example_manage/list/' 
    auth_type='job'
    return locals()

@login_required
@csrf_exempt
def example_manage_list(request):
    user = request.user
    name = request.GET.get('name', None)
    create_user = request.GET.get('create_user', None)
    created_from = request.GET.get('created_from', None)
    created_to = request.GET.get('created_to', None)
    update_user = request.GET.get('update_user', None)
    updated_from = request.GET.get('updated_from', None)
    updated_to = request.GET.get('updated_to', None)
    
    iDisplayLength = int(request.GET.get('iDisplayLength'))
    iDisplayStart = int(request.GET.get('iDisplayStart'))
    sEcho = int(request.GET.get('sEcho'))
    iSortCol_0 = int(request.GET.get('iSortCol_0',0))
    sSortDir_0 = request.GET.get('sSortDir_0')
    order_list = [None,'name', 'template__name', 'remarks', 'create_user__username', 'created', 'update_user__username', 'updated']
    order_item = order_list[iSortCol_0]

    jobs = _job.Job.objects.filter(
        Q(create_user=user)|Q(id__in=[a[0] for a in Perm.objects.filter(Q(end_time__lte=datetime.datetime.now())|Q(end_time=None),ptype=PERM_PTYPE_JOB,to_user=user,is_delete=False).values_list('object_id')]),
        template__template_type__in=(t[0] for t in USER_TEMPLATE_TYPES),is_delete=False)

    #查询
    if name:
        jobs = jobs.filter(name__icontains = name)
    one_day = datetime.timedelta(days=1)
    if create_user:
        jobs = jobs.filter(create_user__username__icontains = create_user)
    if created_from:
        jobs = jobs.filter(created__gte = created_from)
    if created_to:
        created_to = datetime.datetime.strptime(created_to,'%Y-%m-%d')
        jobs = jobs.filter(created__lte = (created_to+one_day))
    if update_user:
        jobs = jobs.filter(update_user__username__icontains = update_user)
    if updated_from:
        jobs = jobs.filter(updated__gte = updated_from)
    if updated_to:
        updated_to = datetime.datetime.strptime(updated_to,'%Y-%m-%d')
        jobs = jobs.filter(updated__lte = (updated_to+one_day))
    
    #排序
    if order_item:
        if sSortDir_0 == "desc":
            order_item = '-%s' % order_item
        jobs = jobs.order_by(order_item)
    else:
        jobs = jobs.order_by('id')
    
    #第一个参数表示需要分页的对象，可为list、tuple、QuerySet，只要它有count()或者__len__()函数
    #第二个参数为每页显示记录数
    p = Paginator(jobs, iDisplayLength)
    total = p.count #总数
    page_range = p.page_range #页数list
    page = p.page(page_range[iDisplayStart / iDisplayLength])
    object_list = page.object_list
    
    sdicts = {}
    sdicts["sEcho"] = sEcho
    sdicts["iTotalRecords"] = total
    sdicts["iTotalDisplayRecords"] = total
    sdicts["aaData"] = []
    for obj in object_list:
        #封装数组，按照列数填入对应的值
#        check_html = u"<input type='checkbox' name='sonCkb' value='%s' id='sonCkb'/>" % obj.id
        box_field = '<td class="text-center"><input class="jobcontent_checked_it" value="{0}" type="checkbox"></td>'.format(obj.id)
        job_name = '<a style="color: blue;" href="javascript:void(0)" onclick="javascript:job_view(\'%s\');">%s</a>' % (obj.id, obj.name)
        template_name = '<a style="color: blue;" href="javascript:void(0)" onclick="javascript:template_view(\'%s\');">%s</a>' % (obj.template.id, obj.template.name)
        created = obj.created.strftime('%Y-%m-%d %H:%M:%S') if obj.created else ""
        updated = obj.updated.strftime('%Y-%m-%d %H:%M:%S') if obj.updated else ""
        # operation = u'<a style="color: blue;" href="javascript:void(0)">授权</a>'
        data = [box_field,job_name, template_name, obj.remarks, obj.create_user.username if obj.create_user else "", created, obj.update_user.username if obj.update_user else "", updated]
        sdicts["aaData"].append(data)
    return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))


from django.conf.urls import patterns, url
urlpatterns = patterns('',
    url(r'^example_manage/$', example_manage_index),
    url(r'^example_manage/list/$', example_manage_list),
)
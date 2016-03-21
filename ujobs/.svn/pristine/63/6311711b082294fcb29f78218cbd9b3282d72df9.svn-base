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
from service import _template
import datetime
from utils.ctranslate import LazyEncoder
from enums.enum_template import USER_TEMPLATE_TYPES
from enums.enum_account import PERM_PTYPE_TEMPLATE
from django.db.models import Q
from apps.accounts.models import Perm
from settings import SPECIAL_USERS

@login_required
@csrf_exempt
@render_to('job_manage/contentDiv.html')
def job_manage_index(request):
    # table_fields = [u'作业实例名称', u'作业类型',u'所属业务', u'备注', u'步骤数量', u'创建人', u'创建时间', u'最后修改人', u'最后修改时间',u'已授权用户',u'操作']
    table_fields = [u'作业实例名称', u'作业类型',u'所属业务', u'备注', u'步骤数量', u'创建人', u'最后修改人', u'已授权用户',u'操作']
    ajax_url = u'/job_manage/list/'
    auth_type='template'
    return locals()

@login_required
@csrf_exempt
def job_manage_list(request):
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
    # order_list = [None,'name', 'template__template_type','template__work_type','remarks', None,'create_user__username', 'created', 'update_user__username', 'updated',None,None]
    order_list = [None,'name', 'template_type','work_type','remarks', None,'create_user__username', 'update_user__username', None,None]
    order_item = order_list[iSortCol_0]
    
    if user.username in SPECIAL_USERS:
        templates = _template.get_templates_by_params(template_type__in=(t[0] for t in USER_TEMPLATE_TYPES),is_delete=False)
    else:
        templates = _template.Template.objects.filter(\
            Q(create_user=user)|Q(id__in=[a[0] for a in Perm.objects.filter(Q(end_time__lte=datetime.datetime.now())|Q(end_time=None),ptype=PERM_PTYPE_TEMPLATE,to_user=user,is_delete=False).values_list('object_id')]),\
            template_type__in=(t[0] for t in USER_TEMPLATE_TYPES),is_delete=False)

    #查询
    if name:
        templates = templates.filter(name__icontains = name)
    one_day = datetime.timedelta(days=1)
    if create_user:
        templates = templates.filter(create_user__username__icontains = create_user)
    if created_from:
        templates = templates.filter(created__gte = created_from)
    if created_to:
        created_to = datetime.datetime.strptime(created_to,'%Y-%m-%d')
        templates = templates.filter(created__lte = (created_to+one_day))
    if update_user:
        templates = templates.filter(update_user__username__icontains = update_user)
    if updated_from:
        templates = templates.filter(updated__gte = updated_from)
    if updated_to:
        updated_to = datetime.datetime.strptime(updated_to,'%Y-%m-%d')
        templates = templates.filter(updated__lte = (updated_to+one_day))

    #排序
    if order_item:
        if sSortDir_0 == "desc":
            order_item = '-%s' % order_item
        templates = templates.order_by(order_item)
    else:
        templates = templates.order_by('-updated')

    #第一个参数表示需要分页的对象，可为list、tuple、QuerySet，只要它有count()或者__len__()函数
    #第二个参数为每页显示记录数
    p = Paginator(templates, iDisplayLength)
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
        template_name = '<a style="color: blue;" href="javascript:void(0)" onclick="javascript:job_view_v2(\'%s\');">%s</a>' % (obj.id, obj.name)
        template_type = obj.get_template_type_display()
        work_type = obj.work_type
        step_num = _template.get_templateSteps_by_params(template=obj,is_checked=True,is_delete=False).count()
        created = obj.created.strftime('%Y-%m-%d %H:%M:%S') if obj.created else ""
        updated = obj.updated.strftime('%Y-%m-%d %H:%M:%S') if obj.updated else ""

        # operation = u'<a style="color: blue;" href="javascript:void(0)">授权</a>'
        perms = Perm.objects.filter(object_id=obj.id,ptype=PERM_PTYPE_TEMPLATE,is_delete=False)
        to_usernames = ','.join([perm.to_user.first_name for perm in perms]) if perms else ""
        operation = '<td><a onclick="job_copy_v2(%s)" href="javascript:void(0)">复制</a>&nbsp;<a onclick="job_delete_v2(%s)" href="javascript:void(0)">删除</a></td>'%(obj.id,obj.id)
        # data = [box_field,template_name, template_type,work_type,obj.remarks, step_num,obj.create_user.username if obj.create_user else "", created, obj.update_user.username if obj.update_user else "", updated,to_usernames,operation]
        data = [box_field,template_name, template_type,work_type,obj.remarks, step_num,obj.create_user.username if obj.create_user else "", obj.update_user.username if obj.update_user else "", to_usernames,operation]
        sdicts["aaData"].append(data)
    return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))


from django.conf.urls import patterns, url
urlpatterns = patterns('',
    url(r'^job_manage/$', job_manage_index),
    url(r'^job_manage/list/$', job_manage_list),
)
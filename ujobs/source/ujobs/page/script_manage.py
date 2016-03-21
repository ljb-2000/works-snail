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
from service import _script
import datetime
from utils.ctranslate import LazyEncoder
from django.db.models import Q
from apps.accounts.models import Perm
from enums.enum_account import PERM_PTYPE_SCRIPT
from settings import SPECIAL_USERS

@login_required
@csrf_exempt
@render_to('script_manage/contentDiv.html')
def script_manage_index(request):
    # table_fields = [u'脚本名称', u'脚本描述', u'创建人', u'创建时间', u'最后修改人', u'最后修改时间', u'操作']
    table_fields = [u'脚本名称', u'脚本描述', u'创建人', u'最后修改人', u'已授权用户', u'操作']
    ajax_url = u'/script_manage/list/'
    auth_type='script'
    return locals()

@login_required
@csrf_exempt
def script_manage_list(request):
    user = request.user
    name = request.GET.get('name', None)
    describe = request.GET.get('describe', None)
    create_user = request.GET.get('create_user', None)
    created_from = request.GET.get('created_from', None)
    created_to = request.GET.get('created_to', None)
    
    iDisplayLength = int(request.GET.get('iDisplayLength'))
    iDisplayStart = int(request.GET.get('iDisplayStart'))
    sEcho = int(request.GET.get('sEcho'))
    iSortCol_0 = int(request.GET.get('iSortCol_0',0))
    sSortDir_0 = request.GET.get('sSortDir_0')
    # order_list = [None,'name', 'describe', 'create_user__username', 'created', 'update_user__username', 'updated', None]
    order_list = [None,'name', 'describe', 'create_user__username', 'update_user__username', None, None]
    order_item = order_list[iSortCol_0]
    
    if user.username in SPECIAL_USERS:
        scripts = _script.get_scripts_by_params(is_once=False,is_delete=False)
    else:
        scripts = _script.Script.objects.filter(\
        Q(create_user=user)|Q(id__in=[a[0] for a in Perm.objects.filter(Q(end_time__lte=datetime.datetime.now())|Q(end_time=None),ptype=PERM_PTYPE_SCRIPT,to_user=user,is_delete=False).values_list('object_id')]),\
        is_once=False,is_delete=False)

#    #查询
    if name:
        scripts = scripts.filter(name__icontains = name)
    if describe:
        scripts = scripts.filter(describe__icontains = describe)
    one_day = datetime.timedelta(days=1)
    if create_user:
        scripts = scripts.filter(create_user__username__icontains = create_user)
    if created_from:
        scripts = scripts.filter(created__gte = created_from)
    if created_to:
        created_to = datetime.datetime.strptime(created_to,'%Y-%m-%d')
        scripts = scripts.filter(created__lte = (created_to+one_day))
    
    #排序
    if order_item:
        if sSortDir_0 == "desc":
            order_item = '-%s' % order_item
        scripts = scripts.order_by(order_item)
    else:
        scripts = scripts.order_by('-updated')
    
    #第一个参数表示需要分页的对象，可为list、tuple、QuerySet，只要它有count()或者__len__()函数
    #第二个参数为每页显示记录数
    p = Paginator(scripts, iDisplayLength)
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
        box_field = '<td class="text-center"><input class="scriptcontent_checked_it" value="{0}" type="checkbox"></td>'.format(obj.id)
        script_name = '<a style="color: blue;" href="javascript:void(0)" onclick="javascript:script_manage_view(\'%s\');">%s</a>' % (obj.id, obj.name)
        created= obj.created.strftime('%Y-%m-%d %H:%M:%S') if obj.created else ""
        updated = obj.updated.strftime('%Y-%m-%d %H:%M:%S') if obj.updated else ""
        operation = u'<a style="color: blue;" href="javascript:void(0)" onclick="javascript:script_manage_delete(\'{0}\');">删除</a>'.format(obj.id)
        perms = Perm.objects.filter(object_id=obj.id,ptype=PERM_PTYPE_SCRIPT,is_delete=False)
        to_usernames = ','.join([perm.to_user.first_name for perm in perms]) if perms else ""

        # data = [box_field,script_name, obj.describe, obj.create_user.username, created, obj.update_user.username, updated, operation ]
        data = [box_field,script_name, obj.describe, obj.create_user.username, obj.update_user.username, to_usernames,operation ]
        sdicts["aaData"].append(data)
    return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))

from django.conf.urls import patterns, url
urlpatterns = patterns('',
    url(r'^script_manage/$', script_manage_index),
    url(r'^script_manage/list/$', script_manage_list),
)
# -- encoding=utf-8 --
import os, sys
from apps.accounts.models import Perm

sys.path.insert(0, os.path.abspath(os.curdir))

from utils.decorator import render_to, login_required
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from django.core.paginator import Paginator
from service import _template,_job
import datetime, traceback
from enums import enum_template, enum_account
from utils.ctranslate import LazyEncoder
from django.db.models import Q

@login_required
@csrf_exempt
@render_to('md_manage/contentDiv.html')
def md_manage_index(request):
    table_fields = [u'模板名', u'模板类型',u'所属业务', u'备注', u'步骤数量', u'创建人', u'创建时间', u'最后修改人', u'最后修改时间']
    ajax_url = u'/md_manage/list/'
    auth_type='template'
    return locals()

@login_required
@csrf_exempt
def md_manage_list(request):
    user = request.user
    data = request.GET
    template_name = data.get("template_name",None)
    template_creator = data.get("template_creator",None)
    template_type = data.get("template_type","")
    template_step = data.get("template_step",None)
    template_stime = data.get("template_stime",None)
    template_etime = data.get("template_etime",None)
    id_search_type = data.get("id_search_type",None)
    id_search_value = data.get("id_search_value",None)

    iDisplayLength = int(request.GET.get('iDisplayLength'))
    iDisplayStart = int(request.GET.get('iDisplayStart'))
    sEcho = int(request.GET.get('sEcho'))
    iSortCol_0 = int(request.GET.get('iSortCol_0',0))
    sSortDir_0 = request.GET.get('sSortDir_0')
    order_list = [None,'name', 'template_type', 'work_type', None, None,'create_user__username','created', 'update_user__username', 'updated', None]
    order_item = order_list[iSortCol_0]

    templates = _template.Template.objects.filter(
        Q(create_user=user)|Q(id__in=[a[0] for a in Perm.objects.filter(Q(end_time__lte=datetime.datetime.now())|Q(end_time=None),ptype=enum_account.PERM_PTYPE_TEMPLATE,to_user=user,is_delete=False).values_list('object_id')]),
        template_type__in=(t[0] for t in enum_template.USER_TEMPLATE_TYPES),is_delete=False)

    if id_search_type == 'template' and id_search_value:
        templates = templates.filter(id=id_search_value)
    if id_search_type == 'job' and id_search_value:
        ids = _job.Job.objects.filter(id=id_search_value).values_list('template__id')
        templates = templates.filter(id__in=[a[0] for a in ids])
    if template_name:
        templates = templates.filter(name__icontains=template_name)
    one_day = datetime.timedelta(days=1)
    if template_creator:
        templates = templates.filter(create_user__username__icontains=template_creator)
    if template_stime and template_stime!="undefined":
        templates = templates.filter(created__gte=template_stime)
    if template_etime and template_etime!="undefined":
        created_to = datetime.datetime.strptime(template_etime, '%Y-%m-%d')
        templates = templates.filter(created__lte=(created_to + one_day))
    if template_type != "" :
        print "template===========",template_type,template_type != None
        templates = templates.filter(template_type=template_type)
    if template_step:
        steps = _template.TemplateStep.objects.filter(template__in=templates,name__icontains=template_step).values_list('template__id')
        templates = templates.filter(id__in=[a[0] for a in steps])
    #排序
    if order_item:
        if sSortDir_0 == "desc":
            order_item = '-%s' % order_item
        templates = templates.order_by(order_item)
    else:
        templates = templates.order_by('id')

    p = Paginator(templates, iDisplayLength)
    total = p.count #总数
    page_range = p.page_range #页数list

    sdicts = {}
    sdicts["sEcho"] = sEcho
    sdicts["iTotalRecords"] = total
    sdicts["iTotalDisplayRecords"] = total
    sdicts["aaData"] = []
    if len(page_range)==0:
        return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))
    page = p.page(page_range[iDisplayStart / iDisplayLength])
    object_list = page.object_list

    for obj in object_list:
        box_field = '<td class="text-center"><input class="mdcontent_checked_it" value="{0}" type="checkbox"></td>'.format(obj.id)
        template_name = u'<a style="color: blue;" href="javascript:void(0)" onclick="template_view(\'%s\');">%s</a>' % (obj.id, obj.name)
        template_steps_num = _template.get_templateSteps_by_params(template=obj,is_delete=False).count()
        created_time = obj.created.strftime('%Y-%m-%d %H:%M:%S') if obj.created else ""
        updated_time = obj.updated.strftime('%Y-%m-%d %H:%M:%S') if obj.updated else ""
        # operation = u'<a style="color: blue;" href="javascript:void(0)">授权</a>'
        data = [box_field,template_name, "" if obj.template_type==None else obj.get_template_type_display(), obj.work_type, obj.remarks, template_steps_num, "" if not obj.create_user else obj.create_user.username, created_time, "" if not obj.update_user else obj.update_user.username, updated_time]
        sdicts["aaData"].append(data)
    return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))


from django.conf.urls import patterns, url
urlpatterns = patterns('',
    url(r'^md_manage/$', md_manage_index),
    url(r'^md_manage/list/$', md_manage_list),
)
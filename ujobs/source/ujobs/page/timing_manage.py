# -- encoding=utf-8 --
import os, sys
from django.template.loader import render_to_string

sys.path.insert(0, os.path.abspath(os.curdir))

from utils.decorator import render_to, login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
import json
from django.core.paginator import Paginator
from service import _template, _job, _history
import datetime
from utils.ctranslate import LazyEncoder
from enums.enum_template import *
from settings import TIME_FMT, scheduler, SPECIAL_USERS
import traceback, logging
from utils.utils import handle_job_schedule
from apps.jobs.models import ScheduleJobs,APScheduleJobs
from apps.jobs.views import job_sync_v2

logger = logging.getLogger('logger')

@login_required
@csrf_exempt
@render_to('timing_manage/contentDiv.html')
def timing_manage_index(request):
    # table_fields = [u'模板', u'作业实例', u'业务', u'定时表达式', u'当前状态', u'任务描述', u'启动人', u'创建人', u'创建时间', u'操作']
    table_fields = [u'作业实例', u'业务', u'定时表达式', u'当前状态', u'任务描述', u'启动人', u'创建人', u'创建时间', u'操作']
    ajax_url = u'/timing_manage/list/'
    return locals()

@login_required
@csrf_exempt
def timing_manage_list(request):
    try:
        logger.debug("current job status: {0}".format(scheduler.print_jobs()))
    except:
        error = traceback.format_exc()
        logger.error(error)
        print error
    name = request.GET.get('name', None)
    creator = request.GET.get('creator', None)
    executor = request.GET.get('executor', None)
    note = request.GET.get('note', None)
    status = request.GET.get('status', None)
    stime = request.GET.get('stime', None)
    etime = request.GET.get('etime', None)

    iDisplayLength = int(request.GET.get('iDisplayLength'))
    iDisplayStart = int(request.GET.get('iDisplayStart'))
    sEcho = int(request.GET.get('sEcho'))
    iSortCol_0 = int(request.GET.get('iSortCol_0',0))
    sSortDir_0 = request.GET.get('sSortDir_0')
    order_list = [ None, None, None, None, None, None, None, None, None]
    order_item = order_list[iSortCol_0]
    user = request.user
    jobs = _job.ScheduleJobs.objects.filter(creator=user).exclude(status=SCHEDULE_STATUS_DELETE)

    # 查询
    if name:
        jobs = jobs.filter(job__name__icontains=name)
    if note:
        jobs = jobs.filter(note__icontains=note)
    one_day = datetime.timedelta(days=1)
    if creator:
        jobs = jobs.filter(creator__username__icontains=creator)
    if executor:
        jobs = jobs.filter(executor__username__icontains=executor)
    if status and status != "all":
        status = SCHEDULE_STATUS_STARTED if status == 'start' else SCHEDULE_STATUS_PAUSE if status == "pause" else SCHEDULE_STATUS_FINISHED
        jobs = jobs.filter(status__eq=status)
    if stime:
        jobs = jobs.filter(created__gte=stime)
    if etime:
        created_to = datetime.datetime.strptime(etime, '%Y-%m-%d')
        jobs = jobs.filter(created__lte=(created_to + one_day))
    
    #排序
    if order_item:
        if sSortDir_0 == "desc":
            order_item = '-%s' % order_item
        jobs = jobs.order_by(order_item)
    else:
        jobs = jobs.order_by("-updated")
    
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
        template_name = u'<a style="color: blue;" href="javascript:void(0)" onclick="template_view(\'%s\');">%s</a>' % (obj.job.template.id, obj.job.template.name)
        job_name = '<a style="color: blue;" href="javascript:void(0)" onclick="javascript:job_view(\'%s\');">%s</a>' % (obj.job.id, obj.job.name)
        operation = u'<a href="javascript:void(0);" onclick="show_schedule_edit(\'{0}\')" data-toggle="modal" data-target="#modify_timing">修改</a>&nbsp;<a href="javascript:void(0);" onclick="schedule_delete(\'{0}\')">删除</a>&nbsp;<a href="javascript:void(0);" onclick="schedule_toggle(\'{0}\',\'{2}\')">{1}</a>'.format(obj.id, u'启动' if obj.status == SCHEDULE_STATUS_PAUSE else u"暂停",'resume' if obj.status == SCHEDULE_STATUS_PAUSE else u"pause")

        data = [job_name, obj.job.template.work_type or u"未分类", obj.expression, obj.get_status_display(),
                obj.note, obj.executor.username,obj.creator.username,obj.created.strftime(TIME_FMT),operation]
        sdicts["aaData"].append(data)
    return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))

@login_required
@require_POST
@csrf_exempt
def schedule_delete(request,task_id):
    user = request.user
    status = 500
    data = {}
    msg = ""
    try:
        task = _job.get_scheduleJob_by_params(id=task_id)
        if not task:
            msg = u"任务不存在"
            raise Exception(msg)
        if user != task.creator:
            msg = u"无权限操作"
            raise Exception(msg)
        if request.method == 'POST':
            try:
                schedule_id = task.schedule_id
                logger.debug("### start toggle schedule job, task_id:{0}, schedule_id:{1}".format(task.id,schedule_id))
                aps_job = scheduler.get_job(schedule_id)
                if aps_job:
                    scheduler.remove_job(schedule_id)
                else:
                    logger.warning("### bg task not exist, ignore aps remove_job call.")
                task.status = SCHEDULE_STATUS_DELETE
                task.save()
                status = 200
                msg = u"定时任务删除成功"
            except Exception,e:
                msg = e.message
                error = traceback.format_exc()
                logger.error(error)
        else:
            msg = u"请求方式错误"
    except Exception,e:
        if not msg:
            error = traceback.format_exc()
            logger.error(error)
            msg = u"处理出错"
    data['msg']=msg
    return HttpResponse(json.dumps({
        "status": status,
        "result": data
    }))

@login_required
@require_POST
@csrf_exempt
def schedule_toggle(request,task_id,action):
    user = request.user
    status = 500
    data = {}
    msg = ""
    try:
        task = _job.get_scheduleJob_by_params(id=task_id)
        if not task:
            msg = u"任务不存在"
            raise Exception(msg)
        if user != task.creator:
            msg = u"无权限操作"
            raise Exception(msg)
        if action not in ["pause",'resume']:
            msg = u"操作方式错误"
            raise Exception(msg)
        if request.method == 'POST':
            try:
                schedule_id = task.schedule_id
                logger.debug("### start toggle schedule job, task_id:{0}, schedule_id:{1}".format(task.id,schedule_id))
                # check if APSchedule job is missing.
                missing = True if not schedule_id or not scheduler.get_job(schedule_id) else False
                if missing:
                    logger.warning("APSchedule job missing, start create new job...")
                    parts = task.expression.split(" ")
                    aps_job = scheduler.add_job(handle_job_schedule,trigger="cron",
                            second=parts[0],minute=parts[1],hour=parts[2],
                            day_of_week=parts[3],day=parts[4],month=parts[5],
                            year=parts[6],args=[task.job.id,user.username,task.id])
                    schedule_id = aps_job.id
                    task.schedule_id = schedule_id
                if action == 'pause':
                    logger.debug("start pause job...")
                    scheduler.pause_job(schedule_id)
                    task.status = SCHEDULE_STATUS_PAUSE
                if action == 'resume':
                    logger.debug("start resume job...")
                    scheduler.resume_job(schedule_id)
                    task.status = SCHEDULE_STATUS_STARTED
                task.save()
                status = 200
                msg = u"定时任务修改成功"
            except Exception,e:
                msg = e.message
                error = traceback.format_exc()
                logger.error(error)
        else:
            msg = u"请求方式错误,只能为POST"
    except Exception,e:
        if not msg:
            error = traceback.format_exc()
            logger.error(error)
            msg = u"处理出错"
    data['msg']=msg
    return HttpResponse(json.dumps({
        "status": status,
        "result": data
    }))

@login_required
@csrf_exempt
def schedule_modify(request,task_id):
    user = request.user
    status = 500
    data = {}
    task = _job.get_scheduleJob_by_params(id=task_id)
    if not task:
        msg = u"任务不存在"
    else:
        if request.method == 'GET':
            template_file = "timing_manage/timing_modal.html"
            html = render_to_string(template_file, locals())
            msg = u'ok'
            data['html'] = html
            status = 200
        elif request.method == 'POST':
            try:
                expression = request.POST.get("task_expression","").strip()
                note = request.POST.get("task_note","")
                parts = expression.split(" ")
                logger.debug("### start reschedule job, task_id:{0}".format(task.id))
                missing = True if APScheduleJobs.objects.filter(id=task.schedule_id).count()==0 else False
                if task.expression != expression or missing:
                    if len(parts) == 7:
                        if missing:
                            logger.warning("APSchedule job missing, start create new job...")
                            sch_job = scheduler.add_job(handle_job_schedule,trigger="cron",
                                                    second=parts[0],minute=parts[1],hour=parts[2],
                                                    day_of_week=parts[3],day=parts[4],month=parts[5],
                                                    year=parts[6],args=[task.job.id,user.username,task.id])
                            task.schedule_id = sch_job.id
                            if task.status == SCHEDULE_STATUS_PAUSE:
                                sch_job.pause()
                        else:
                            logger.debug("expression changed, start reschedule job")
                            scheduler.reschedule_job(task.schedule_id,trigger="cron",
                                                    second=parts[0],minute=parts[1],hour=parts[2],
                                                    day_of_week=parts[3],day=parts[4],month=parts[5],
                                                    year=parts[6])
                    else:
                        msg = u"表达式错误"
                        logger.error("expression:{0}".format(expression))
                        raise Exception(msg)
                else:
                    logger.debug("expression no change, no change to schedule job.")
                task.updated = datetime.datetime.now()
                task.expression = expression
                task.note = note
                task.save()
                status = 200
                msg = u"定时任务修改成功"
            except Exception,e:
                msg = e.message
                error = traceback.format_exc()
                logger.error(error)
        else:
            msg = u"请求方式错误,只能为GET,POST"
    data['msg']=msg
    return HttpResponse(json.dumps({
        "status": status,
        "result": data
    }))

@login_required
@csrf_exempt
def schedule_add(request,job_id):
    status = 500
    data = {}
    msg = ""
    try:
        user = request.user
        job = _job.get_job_by_params(id=job_id)
        if not job:
            msg = u"作业不存在"
        else:
            if request.method == 'GET':
                check_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                template_file = "example_manage/timing_modal.html"
                html = render_to_string(template_file, locals())
                data['html'] = html
                data['msg'] = u'ok'
                data['check_id'] = check_id
                status = 200
            elif request.method == 'POST':
                expression = request.POST.get("expression","")
                note = request.POST.get("note","")
                parts = expression.split(" ")
                task = None
                sch_job = None
                try:
                    if len(parts) == 7:
                        task = ScheduleJobs.objects.create(creator=user,executor=user,job=job,expression=expression,note=note,status=SCHEDULE_STATUS_STARTED)
                        sch_job = scheduler.add_job(handle_job_schedule,trigger="cron",
                                                    second=parts[0],
                                                    minute=parts[1],
                                                    hour=parts[2],
                                                    day_of_week=parts[3],
                                                    day=parts[4],
                                                    month=parts[5],
                                                    year=parts[6],
                                                    args=[job_id,user.username,task.id])
                    else:
                        msg = u"表达式格式错误"
                        raise Exception(msg)
                    task.schedule_id = sch_job.id
                    task.save()
                    status = 200
                    msg = "add ok."
                except Exception,e:
                    msg = e.message
                    error = traceback.format_exc()
                    logger.error(error)
                if not sch_job and task: task.delete()
            else:
                msg = u"请求方式非法"
    except:
        if not msg:
            error = traceback.format_exc()
            logger.error(error)
            print error
        pass
    data['msg'] = msg if msg else u"创建失败"
    return HttpResponse(json.dumps({
        "status": status,
        "result": data
    }, cls=LazyEncoder))

@login_required
@csrf_exempt
@render_to('timing_manage/timing_history.html')
def timing_history_index(request):
    table_fields = [u'作业实例', u'任务描述', u'定时表达式', u'启动结果', u'启动信息', u'启动人', u'触发时间']
    ajax_url = u'/timing_manage/history_list/'
    return locals()

@login_required
@csrf_exempt
def timing_history_list(request):
    """
        history for schedule list.
    """
    name = request.GET.get('name', None)
    note = request.GET.get('note', None)
    executor = request.GET.get('executor', None)
    result = request.GET.get('result_type', None)
    stime = request.GET.get('stime', None)
    etime = request.GET.get('etime', None)

    iDisplayLength = int(request.GET.get('iDisplayLength'))
    iDisplayStart = int(request.GET.get('iDisplayStart'))
    sEcho = int(request.GET.get('sEcho'))
    iSortCol_0 = int(request.GET.get('iSortCol_0',0))
    sSortDir_0 = request.GET.get('sSortDir_0')
    order_list = ["task__job__name", None, None, None, None, None, None]
    order_item = order_list[iSortCol_0]
    user = request.user

    histories = _history.get_scheduleHistorys_by_params(task__creator=user) if user.username not in SPECIAL_USERS else _history.get_scheduleHistorys_by_params()

    # 查询
    if name:
        histories = histories.filter(task__job__name__icontains=name)
    if note:
        histories = histories.filter(task__note__icontains=note)
    one_day = datetime.timedelta(days=1)
    if result:
        histories = histories.filter(result=result)
    if executor:
        histories = histories.filter(task__creator__username__icontains=executor)
    if stime:
        histories = histories.filter(trigger_time__gte=stime)
    if etime:
        created_to = datetime.datetime.strptime(etime, '%Y-%m-%d')
        histories = histories.filter(trigger_time__lte=(created_to + one_day))

    #排序
    if order_item:
        if sSortDir_0 == "desc":
            order_item = '-%s' % order_item
        histories = histories.order_by(order_item)
    else:
        histories = histories.order_by("-trigger_time")

    p = Paginator(histories, iDisplayLength)
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
        # job_name = '<a style="color: blue;" href="javascript:void(0)" onclick="javascript:job_view(\'%s\');">%s</a>' % (obj.task.job.id, obj.task.job.name)
        name = u'<a style="color: blue;" href="javascript:void(0)" onclick="javascript:show_result(\'{0}\');">{1}</a>'.format(obj.history.id,obj.history.name) if obj.history else u'未生成历史记录'
        data = [name,obj.task.note,obj.task.expression,obj.get_result_display(),obj.info,obj.task.creator.username,obj.trigger_time.strftime(TIME_FMT)]
        sdicts["aaData"].append(data)
    return HttpResponse(json.dumps(sdicts))

@login_required
@csrf_exempt
def schedule_add_v2(request,template_id):
    status = 500
    data = {}
    msg = ""
    try:
        user = request.user
        
        template = _template.get_template_by_params(id=template_id)
        if not template:
            msg = u"作业不存在"
        else:
            job = job_sync_v2(template)
            if request.method == 'GET':
                check_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                template_file = "job_manage/timing_modal.html"
                html = render_to_string(template_file, locals())
                data['html'] = html
                data['msg'] = u'ok'
                data['check_id'] = check_id
                status = 200
            elif request.method == 'POST':
                expression = request.POST.get("expression","")
                note = request.POST.get("note","")
                parts = expression.split(" ")
                task = None
                sch_job = None
                try:
                    if len(parts) == 7:
                        task = ScheduleJobs.objects.create(creator=user,executor=user,job=job,expression=expression,note=note,status=SCHEDULE_STATUS_STARTED)
                        sch_job = scheduler.add_job(handle_job_schedule,trigger="cron",
                                                    second=parts[0],
                                                    minute=parts[1],
                                                    hour=parts[2],
                                                    day_of_week=parts[3],
                                                    day=parts[4],
                                                    month=parts[5],
                                                    year=parts[6],
                                                    args=[job_id,user.username,task.id])
                    else:
                        msg = u"表达式格式错误"
                        raise Exception(msg)
                    task.schedule_id = sch_job.id
                    task.save()
                    status = 200
                    msg = "add ok."
                except Exception,e:
                    msg = e.message
                    error = traceback.format_exc()
                    logger.error(error)
                if not sch_job and task: task.delete()
            else:
                msg = u"请求方式非法"
    except:
        if not msg:
            error = traceback.format_exc()
            logger.error(error)
            print error
        pass
    data['msg'] = msg if msg else u"创建失败"
    return HttpResponse(json.dumps({
        "status": status,
        "result": data
    }, cls=LazyEncoder))

from django.conf.urls import patterns, url
urlpatterns = patterns('',
    url(r'^timing_manage/$', timing_manage_index),
    url(r'^timing_manage/list/$', timing_manage_list),
    url(r'^timing_manage/history_list/$', timing_history_list),
    url(r'^timing_manage/history_index/$', timing_history_index),

    url(r'^timing_manage/add/(?P<job_id>\d+)/$', schedule_add),
    url(r'^timing_manage/delete/(?P<task_id>\d+)/$', schedule_delete),
    url(r'^timing_manage/toggle/(?P<task_id>\d+)/(?P<action>\w+)/$', schedule_toggle),
    url(r'^timing_manage/modify/(?P<task_id>\d+)/$', schedule_modify),
    
    url(r'^timing_manage/add_v2/(?P<template_id>\d+)/$', schedule_add_v2),
)
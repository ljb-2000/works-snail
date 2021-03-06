#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Created on 2015-8-20

@author: wx
'''

import os, sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
sys.path.insert(0, os.path.abspath(os.curdir))

from django.utils.translation import ugettext_lazy as _
from utils.decorator import render_to, login_required
from django.db.transaction import commit_on_success
from django.views.decorators.csrf import csrf_exempt
from service import _account, _script, _template, _job, _file, _history, _template
from apps.accounts.forms import AccountForm
from django.http import HttpResponse
import json, traceback, datetime, logging
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from utils.ctranslate import LazyEncoder
from enums import enum_template, enum_account
from utils.utils import get_input_ips,build_hidden_ip_dict, handle_step_pull_file,handle_step_push_file,handle_job
from settings import MAX_UPLOAD_SIZE
from utils.utils import get_online_status
from utils.redisclient import rc
from django.db.models import Q
from apps.accounts.models import Perm
from releaseinfo import IP_KEY_PREFIX, FILE_SERVER_HOST
from apps.template.forms import AddTemplateForm,EditTemplateForm

logger = logging.getLogger('logger')

@login_required
@csrf_exempt
def job_list(request,template_id):
    '''
        显示模板执行态列表.
    '''
    user = request.user
    iDisplayLength = int(request.GET.get('iDisplayLength'))
    iDisplayStart = int(request.GET.get('iDisplayStart'))
    sEcho = int(request.GET.get('sEcho'))
    iSortCol_0 = int(request.GET.get('iSortCol_0',0))
    sSortDir_0 = request.GET.get('sSortDir_0')
    order_list = [None, 'name', 'created', 'create_user__username', None, None]
    order_item = order_list[iSortCol_0]

    jobs = _job.get_jobs_by_params(is_delete=False, create_user=user, template__id=template_id, template__template_type__in= \
                                   [enum_template.TEMPLATE_TYPE0,enum_template.TEMPLATE_TYPE1,enum_template.TEMPLATE_TYPE2,enum_template.TEMPLATE_TYPE3,enum_template.TEMPLATE_TYPE4])

    if order_item:
        if sSortDir_0 == "desc":
            order_item = '-%s' % order_item
        jobs = jobs.order_by(order_item)
    else:
        jobs = jobs.order_by('id')

    p = Paginator(jobs, iDisplayLength)
    total = p.count
    page_range = p.page_range
    page = p.page(page_range[iDisplayStart / iDisplayLength])
    object_list = page.object_list

    sdicts = {}
    sdicts["sEcho"] = sEcho
    sdicts["iTotalRecords"] = total
    sdicts["iTotalDisplayRecords"] = total
    sdicts["aaData"] = []
    for obj in object_list:
        box_field = '<td class="text-center"><input class="md_view_checked_it_%s" value="%s" type="checkbox"></td>'%(template_id,obj.id)
        instance_name = '<a style="color: blue;" href="javascript:void(0)" onclick="job_view(\'%s\');return false;">%s</a>' % (obj.id, obj.name)
        created = datetime.datetime.strftime(obj.created,'%Y-%m-%d %H:%M:%S')
        status = u'<td><i class="font font-error">未同步</i></td>'
        if obj.is_sync:
            status = u'<td><i class="font font-ok">已同步</i></td>'
        operation = '<td><a onclick="job_copy(%s)" href="javascript:void(0)">复制</a>&nbsp;<a onclick="job_delete(%s,%s)" href="javascript:void(0)">删除</a></td>'%(obj.id,obj.id,template_id)
        data = [box_field,instance_name, created, obj.create_user.username, status, operation]
        sdicts["aaData"].append(data)
    return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))

@login_required
@csrf_exempt
@commit_on_success
def job_add(request):
    '''
        add job
    '''
    sdicts = {}
    user = request.user
    code = 500
    now = datetime.datetime.now()
    
    try:
        template_id = request.GET.get('template_id',0)
        template = _template.get_template_by_params(id=template_id)
        templateStep_list = _template.get_templateSteps_by_params(template=template,is_delete=False)
        
        job_name = u'%s 实例 %s'%(template.name,datetime.datetime.strftime(now,'%Y%m%d%H%M%S'))
        job = _job.create_job_by_params(template=template)
        job.name = job_name
        job.create_user = user
        job.update_user = user
        job.mode = template.mode
        job.account = template.account
        job.target = template.target
        job.save()
        
        for templateStep in templateStep_list:
            step_type = templateStep.step_type
            
            jobStep = _job.create_jobStep_by_params(job=job,template_step=templateStep)
            jobStep.name = templateStep.name
            jobStep.describe = templateStep.describe
            jobStep.step_type = templateStep.step_type
            jobStep.order = templateStep.order
            jobStep.is_setting = templateStep.is_setting
            jobStep.account = templateStep.account
            jobStep.target = templateStep.target
            jobStep.is_checked = True
            jobStep.save()
            #脚本步骤
            if step_type == enum_template.STEP_TYPE_SCRIPT:
                sub_step = _template.get_templateStepScript_by_params(step=templateStep)
                new_sub_step = _job.create_jobStepScript_by_params(step=jobStep)
                new_sub_step.version=sub_step.version
                new_sub_step.parameter = sub_step.parameter
                new_sub_step.timeout = sub_step.timeout
                new_sub_step.save()
            #拉取文件
            elif step_type == enum_template.STEP_TYPE_PULL_FILE:
                sub_step = _template.get_templateStepPullFile_by_params(step=templateStep)
                new_sub_step = _job.create_jobStepPullFile_by_params(step=jobStep)
                new_sub_step.limit = sub_step.limit
                new_sub_step.pull_to = sub_step.pull_to
                new_sub_step.pull_to_ip = sub_step.pull_to_ip
                new_sub_step.file_paths = sub_step.file_paths
                new_sub_step.save()
            #分发文件
            elif step_type == enum_template.STEP_TYPE_PUSH_FILE:
                sub_step = _template.get_templateStepPushFile_by_params(step=templateStep)
                new_sub_step = _job.create_jobStepPushFile_by_params(step=jobStep)
                new_sub_step.limit = sub_step.limit
                new_sub_step.push_to = sub_step.push_to
                new_sub_step.save()
                
                templateFileinfos = _template.get_templateFileInfos_by_params(step=templateStep)
                if templateFileinfos:
                    for templateFileinfo in templateFileinfos:
                        jobFileInfo = _job.get_or_create_jobFileInfo_by_params(step=jobStep, remote_ip=templateFileinfo.remote_ip, \
                                                                 push_account=templateFileinfo.push_account, location_type=templateFileinfo.location_type, \
                                                                 remote_path=templateFileinfo.remote_path, record=templateFileinfo.record)[0]
                        jobFileInfo.save()
            #文本步骤
            elif step_type == enum_template.STEP_TYPE_TEXT:
                sub_step = _template.get_templateStepText_by_params(step=templateStep)
                new_sub_step = _job.create_jobStepText_by_params(step=jobStep)
                new_sub_step.describe = sub_step.describe
                new_sub_step.save()
                
        jobStep_list = _job.get_jobSteps_by_params(job=job,is_delete=False).order_by('order')
        code = 200
    except:
        error = traceback.format_exc()
        logger.error(error)
        print error
        code = 500
        sdicts['msg'] = u"添加实例失败！"
    
    accounts = _account.get_accounts_by_params(is_delete=False)
    account_id = job.account.id if job.account else ""
    accountForm = AccountForm()
    target_ips = json.loads(job.target) if job.target else []
    hide_ip_dict = build_hidden_ip_dict(target_ips)
    hide_ip_json = json.dumps(hide_ip_dict)
    
#    ajax_url = "/job/job_step/list/%s/"%job.id
    template_file = "example_manage/job_view.html"
    html = render_to_string(template_file, locals())
    sdicts['status'] = code
    sdicts['template_id'] = template.id
    sdicts['job_id'] = job.id
    sdicts['html'] = html
    return HttpResponse(json.dumps(sdicts))

@login_required
@csrf_exempt
@commit_on_success
def job_view(request):
    '''
        view job
    '''
    sdicts = {}
    user = request.user
    code = 500
    
    if request.method == 'POST':
        try:
            job_id = request.POST.get('job_id',0)
            job_name = request.POST.get('job_name')
            job_remarks = request.POST.get('job_remarks')
            check_list = request.POST.getlist('check_list[]',[])
            
            job = _job.get_job_by_params(id=job_id)
            jobStep_list = _job.get_jobSteps_by_params(job=job,is_delete=False).order_by('order')
            template = job.template
            
            jobs = _job.get_jobs_by_params(create_user=user,template=template,name=job_name,is_delete=False).exclude(id=job.id)
            if jobs:
                return HttpResponse(json.dumps({
                        "status":500,
                        "msg": u"实例名称已存在！"
                    }))
        
            job.name = job_name
            job.remarks = job_remarks
            job.update_user = user
            job.save()
            
            for jobStep in jobStep_list:
                step_type = jobStep.step_type
                if '%s'%jobStep.id in check_list:
                    jobStep.is_checked = True
                else:
                    jobStep.is_checked = False
                jobStep.save()
                
            code = 200
        except:
            error = traceback.format_exc()
            logger.error(error)
            print error
            code = 500
            sdicts['msg'] = u"保存实例失败！"
    else:
        job_id = request.GET.get('job_id',0)
        job = _job.get_job_by_params(id=job_id)
        if job:
            template = job.template
            jobStep_list = _job.get_jobSteps_by_params(job=job,is_delete=False).order_by('order')
            for jobStep in jobStep_list:
                step_type = jobStep.step_type
#                    jobStep.target_status = u'全程目标机器（0/0）'
                #文本步骤
                if step_type == enum_template.STEP_TYPE_TEXT:
                    jobStep.target_status = u'文本步骤无需IP'
                else:
                    if not jobStep.is_checked:
                        jobStep.target_status = u'跳过执行'
                    else:
                        if jobStep.is_setting:
                            ip_set = set(json.loads(jobStep.target) if jobStep.target else [])
                            text = u'步骤手工录入'
                        else:
                            ip_set = set(json.loads(job.target) if job.target else [])
                            text = u'全程手工录入'
                        id_list = list(set([rc.get(IP_KEY_PREFIX+ip) for ip in ip_set]))
                        online_agents_num,offline_agents_num,online_agents,offline_agents = get_online_status(id_list)
                        jobStep.target_status = u'%s（%s/%s）'%(text,offline_agents_num,(online_agents_num+offline_agents_num))
                jobStep.save()
            code = 200
        else:
            code = 500
            sdicts['msg'] = u"查看实例失败！"
    
    accounts = _account.get_accounts_by_params(is_delete=False)
    account_id = job.account.id if job.account else ""
    accountForm = AccountForm()
    target_ips = json.loads(job.target) if job.target else []
    hide_ip_dict = build_hidden_ip_dict(target_ips)
    hide_ip_json = json.dumps(hide_ip_dict)
    
    ajax_url = "/job/job_step/list/%s/"%job.id
    template_file = "example_manage/job_view.html"
    html = render_to_string(template_file, locals())
    sdicts['status'] = code
    sdicts['template_id'] = template.id
    sdicts['job_id'] = job.id
    sdicts['html'] = html
    return HttpResponse(json.dumps(sdicts))

@login_required
@csrf_exempt
def job_delete(request):
    '''
        delete job
    '''
    sdicts = {}
    job_id = request.POST.get('job_id',0)
    user = request.user
    job = _job.get_job_by_params(id=job_id)
    if job:
        job.is_delete = True
        job.update_user = user
        job.save()
        sdicts['result'] = 1
        sdicts['showMsg'] = _(u"删除成功")
    else:
        sdicts = {'result':0}
        sdicts['showMsg'] = _(u"删除失败")
    return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))

@login_required
@csrf_exempt
def job_copy(request):
    '''
        copy version
    '''
    sdicts = {}
    user = request.user
    code = 500
    now = datetime.datetime.now()
    
    try:
        job_id = request.GET.get('job_id',0)
        job_copy = _job.get_job_by_params(id=job_id)
        jobStep_list_copy = _job.get_jobSteps_by_params(job=job_copy,is_delete=False).order_by("order")
        template = job_copy.template
        job_name = u'%s 实例 %s'%(template.name,datetime.datetime.strftime(now,'%Y%m%d%H%M%S'))
        job = _job.create_job_by_params(template=template)
        job.name = job_name
        job.remarks = job_copy.remarks
        job.create_user = user
        job.update_user = user
        job.mode = job_copy.mode
        job.account = job_copy.account
        job.target = job_copy.target
        job.is_sync = job_copy.is_sync
        job.save()
        
        for jobStep_copy in jobStep_list_copy:
            step_type = jobStep_copy.step_type
            
            jobStep = _job.create_jobStep_by_params(job=job,template_step=jobStep_copy.template_step)
            jobStep.name = jobStep_copy.name
            jobStep.describe = jobStep_copy.describe
            jobStep.step_type = jobStep_copy.step_type
            jobStep.order = jobStep_copy.order
            jobStep.is_setting = jobStep_copy.is_setting
            jobStep.account = jobStep_copy.account
            jobStep.target = jobStep_copy.target
            jobStep.is_checked = jobStep_copy.is_checked
            jobStep.is_delete = jobStep_copy.is_delete
            jobStep.save()
            #脚本步骤
            if step_type == enum_template.STEP_TYPE_SCRIPT:
                sub_step = _job.get_jobStepScript_by_params(step=jobStep_copy)
                new_sub_step = _job.create_jobStepScript_by_params(step=jobStep)
                new_sub_step.version=sub_step.version
                new_sub_step.parameter = sub_step.parameter
                new_sub_step.timeout = sub_step.timeout
                new_sub_step.save()
            #拉取文件
            elif step_type == enum_template.STEP_TYPE_PULL_FILE:
                sub_step = _job.get_jobStepPullFile_by_params(step=jobStep_copy)
                new_sub_step = _job.create_jobStepPullFile_by_params(step=jobStep)
                new_sub_step.limit = sub_step.limit
                new_sub_step.pull_to = sub_step.pull_to
                new_sub_step.pull_to_ip = sub_step.pull_to_ip
                new_sub_step.file_paths = sub_step.file_paths
                new_sub_step.save()
            #分发文件
            elif step_type == enum_template.STEP_TYPE_PUSH_FILE:
                sub_step = _job.get_jobStepPushFile_by_params(step=jobStep_copy)
                new_sub_step = _job.create_jobStepPushFile_by_params(step=jobStep)
                new_sub_step.limit = sub_step.limit
                new_sub_step.push_to = sub_step.push_to
                new_sub_step.save()
                
#                jobFileinfo_copy_list = _job.get_jobFileInfos_by_params(step=jobStep_copy)
#                if jobFileinfo_copy_list:
#                    for jobFileinfo_copy in jobFileinfo_copy_list:
#                        jobFileInfo = _job.get_or_create_jobFileInfo_by_params(step=jobStep, remote_ip=jobFileinfo_copy.remote_ip, \
#                                                                 push_account=jobFileinfo_copy.push_account, location_type=jobFileinfo_copy.location_type, \
#                                                                 remote_path=jobFileinfo_copy.remote_path, record=jobFileinfo_copy.record)[0]
#                        jobFileInfo.save()
            #文本步骤
            elif step_type == enum_template.STEP_TYPE_TEXT:
                sub_step = _job.get_jobStepText_by_params(step=jobStep_copy)
                new_sub_step = _job.create_jobStepText_by_params(step=jobStep)
                new_sub_step.describe = sub_step.describe
                new_sub_step.save()
        
        jobStep_list = _job.get_jobSteps_by_params(job=job,is_delete=False).order_by("order")
        code = 200
    except:
        error = traceback.format_exc()
        logger.error(error)
        print error
        code = 500
        sdicts['msg'] = u"复制实例失败！"
    
    accounts = _account.get_accounts_by_params(is_delete=False)
    account_id = job.account.id if job.account else ""
    accountForm = AccountForm()
    target_ips = json.loads(job.target) if job.target else []
    hide_ip_dict = build_hidden_ip_dict(target_ips)
    hide_ip_json = json.dumps(hide_ip_dict)
    
#    ajax_url = "/job/job_step/list/%s/"%job.id
    template_file = "example_manage/job_view.html"
    html = render_to_string(template_file, locals())
    sdicts['status'] = code
    sdicts['template_id'] = template.id
    sdicts['job_id'] = job.id
    sdicts['html'] = html
    return HttpResponse(json.dumps(sdicts))

#@login_required
#@csrf_exempt
#def job_step_list(request,job_id):
#    """
#        show job step list of given job.
#    """
#    data = request.GET
#
#    iDisplayLength = int(data.get('iDisplayLength'))
#    iDisplayStart = int(data.get('iDisplayStart'))
#    sEcho = int(data.get('sEcho'))
#    iSortCol_0 = int(data.get('iSortCol_0',0))
#    sSortDir_0 = data.get('sSortDir_0')
#    order_list = [None,None,None,None,None]
#    order_item = order_list[iSortCol_0]
#
#    job_steps = _job.get_jobSteps_by_params(job__id=job_id).order_by('order')
#    sdicts = {}
#    sdicts["aaData"] = []
#    if iDisplayLength>-1:
#        p = Paginator(job_steps, iDisplayLength)
#        total = p.count #总数
#        page_range = p.page_range #页数list
#        sdicts["sEcho"] = sEcho
#        sdicts["iTotalRecords"] = total
#        sdicts["iTotalDisplayRecords"] = total
#
#        page = p.page(page_range[iDisplayStart / iDisplayLength])
#        object_list = page.object_list
#    else:
#        object_list = job_steps
#
#    for obj in object_list:
#        if obj.is_checked:
#            check = u'<input value="%s" class="jobview-checked-it-%s" type="checkbox" checked>'%(obj.id,obj.job.id)
#        else:
#            check = u'<input value="%s" class="jobview-checked-it-%s" type="checkbox">'%(obj.id,obj.job.id)
#        job_step_name = u'<a href="javascript:void(0)" onclick="job_step_edit(\'%s\',\'%s\');">%s</a>' % (obj.id,"script" if obj.step_type == enum_template.STEP_TYPE_SCRIPT else "", obj.name)
#        target = u'目标机器（0/0）'
#        data = [check, obj.order, job_step_name, obj.get_step_type_display(),target]
#        sdicts["aaData"].append(data)
#    return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))

@login_required
@csrf_exempt
def job_step_edit(request,job_step_id):
    """
        edit job step.
    """
    req = request.POST
    user = request.user
    status = 500
    data = {}
    msg = ""
    try:
        step = _job.get_jobStep_by_params(id=job_step_id)
        if not step:
            msg = u"步骤不存在"
            raise Exception,msg
        if step.job.create_user!=user:
            msg = u"您不是该步骤的所有者"
            raise Exception,msg

        type_value = step.step_type
        template_file = ""
        if type_value == enum_template.STEP_TYPE_SCRIPT:
            template_file = "example_manage/edit_script.html"
            sub_step = _job.get_jobStepScript_by_params(step=step)
            perms = Perm.objects.filter(to_user=user, is_delete=False, ptype=enum_account.PERM_PTYPE_SCRIPT)
            scripts = _script.Script.objects.filter(Q(create_user=user)|Q(pk__in=[perm.object_id for perm in perms]),
                                                    is_delete=False,is_once=False)
            version = sub_step.version
            script = version.script if version else None
            versions = _script.get_versions_by_params(script=script) if script else None
            accounts = _account.get_accounts_by_params(is_delete=False)
            accountForm = AccountForm(auto_id="step_script_%s")
            account_id = step.account.id if step.account else 0

        elif type_value == enum_template.STEP_TYPE_PULL_FILE:
            template_file = "example_manage/edit_pull_file.html"
            sub_step = _job.get_jobStepPullFile_by_params(step=step)
            file_paths = [] if not sub_step.file_paths else json.loads(sub_step.file_paths)

        elif type_value == enum_template.STEP_TYPE_PUSH_FILE:
            template_file = "example_manage/edit_send_file.html"
            sub_step = _job.get_jobStepPushFile_by_params(step=step)
            file_infos = _job.get_jobFileInfos_by_params(step=step)
            local_uploads = file_infos.filter(location_type=enum_template.UPLOAD_TYPE_LOCAL).values('record')
            remote_uploads = file_infos.filter(location_type=enum_template.UPLOAD_TYPE_REMOTE)
            local_ids = "" if not local_uploads else " ".join(str(item.get('record')) for item in local_uploads)+" "
            remote_uploads_str = ""
            if remote_uploads.count()>0:
                remote_dict = {}
                remote_dict['remote'] = [{"name":item.remote_path,"ip":item.remote_ip} for item in remote_uploads]
                remote_uploads_str = json.dumps(remote_dict)
            user = request.user
            max_upload_size = MAX_UPLOAD_SIZE
            fileserver_url = FILE_SERVER_HOST

        elif type_value == enum_template.STEP_TYPE_TEXT:
            template_file = "example_manage/edit_text.html"
            sub_step = _job.get_jobStepText_by_params(step=step)

        if type_value in [enum_template.STEP_TYPE_PULL_FILE,enum_template.STEP_TYPE_PUSH_FILE,enum_template.STEP_TYPE_SCRIPT]:
            target_ips = json.loads(step.target) if step.target else []
            hide_ip_dict = build_hidden_ip_dict(target_ips)
            hide_ip_json = json.dumps(hide_ip_dict)

        status=200
        data['html'] = render_to_string(template_file,locals())
        data['name'] = step.name
    except Exception,e:
        data['msg'] = msg if msg else u"步骤信息获取失败"
        error = traceback.format_exc()
        logger.error(error)
        print error
    return HttpResponse(json.dumps({
            "status":status,
            "result":data
    }, cls=LazyEncoder))

@login_required
@csrf_exempt
def job_step_save(request,job_step_id):
    """
        save job step.
    """

    req = request.POST
    user = request.user
    status = 500
    data = {}
    msg = ""
    logger.debug("start template step save...")
    try:
        step = _job.get_jobStep_by_params(id=job_step_id)
        if not step:
            msg = u"步骤不存在"
            raise
        if step.job.create_user!=user:
            msg = u"您不是该步骤的所有者"
            raise

        type_value = step.step_type
        sub_step = None
        if type_value == enum_template.STEP_TYPE_SCRIPT:
            sub_step = _job.get_jobStepScript_by_params(step=step)
            version_id = req.get("step_version","")
            parameter = req.get("parameter","")
            timeout = req.get("timeout",0)
            if version_id and version_id:
                version = _script.get_version_by_params(id=version_id)
                sub_step.version = version
            sub_step.parameter = "" if not parameter else parameter
            sub_step.timeout = 0 if not timeout else timeout

        elif type_value == enum_template.STEP_TYPE_PULL_FILE:
            sub_step = _job.get_jobStepPullFile_by_params(step=step)
            target_path = req.get("pull_file_target_path","")
            pull_to_ip = req.get("pull_to_ip","")
            src_paths = req.get("edit_pullfile_hide","")
            path_list = list(set(src_paths.split(",")))
            path_list = sorted(path_list)
            sub_step.pull_to = target_path
            sub_step.pull_to_ip = pull_to_ip
            sub_step.file_paths = json.dumps(path_list)

        elif type_value == enum_template.STEP_TYPE_PUSH_FILE:
            sub_step = _job.get_jobStepPushFile_by_params(step=step)
            send_file_target_path = req.get("send_file_target_path","")
            record_local_ids_data = req.get("edit_sendfile_record","")
            send_file_remote_json = req.get("send_file_remote_files_list",{})

            sub_step.push_to = send_file_target_path
            file_info_ids = set()
            ### add remote file info.
            if send_file_remote_json:
                send_file_remote_json = json.loads(send_file_remote_json)
                send_file_remote_json = send_file_remote_json.get("remote",[])
                if send_file_remote_json:
                    for item in send_file_remote_json:
                        path = item.get("name","").strip()
                        remote_ip = item.get("ip","").strip()
#                        remote_account = item.get("account_id","").strip()
                        remote_account = None
                        file_info,_ = _job.get_or_create_jobFileInfo_by_params(step=step,
                                                             remote_ip=remote_ip, remote_path=path,
                                                             location_type=enum_template.UPLOAD_TYPE_REMOTE,
                                                             push_account=remote_account)
                        file_info_ids.add(file_info.id)

            # add local file record ids.
            if record_local_ids_data:
                record_local_ids_data = record_local_ids_data.strip(' ')
                record_local_ids = record_local_ids_data.split(' ')
                for record_id in record_local_ids:
                    record = _file.get_uploadRecord_by_params(pk=record_id)
                    file_info,_ = _job.get_or_create_jobFileInfo_by_params(step=step,
                                                               remote_ip=record.src_ip, remote_path=record.remote_path,
                                                               location_type=enum_template.UPLOAD_TYPE_LOCAL)
                    file_info.record = record
                    file_info.save()
#                    print "==== id: ",file_info.id
                    file_info_ids.add(file_info.id)

            #### delete old pushfileinfo records.
            _job.JobFileInfo.objects.filter(step=step).exclude(pk__in=file_info_ids).delete()


        elif type_value == enum_template.STEP_TYPE_TEXT:
            sub_step = _template.get_templateStepText_by_params(step=step)

        if type_value in [enum_template.STEP_TYPE_PULL_FILE,enum_template.STEP_TYPE_PUSH_FILE,enum_template.STEP_TYPE_SCRIPT]:
            step.is_setting = 0
            if req.get("dst_use_own",""):
                ips_json = req.get('target_ips_hide',"")
                ip_set = get_input_ips(ips_json)
                step.target = json.dumps(list(ip_set))
                step.is_setting = 1
                if type_value == enum_template.STEP_TYPE_SCRIPT:
                    account_id = req.get("job_account","")
                    if account_id:
                        account = _account.get_account_by_params(id=int(account_id))
                        step.account = account
                
#        step.name = req.get("step_name",step.name)
#        step.describe = req.get("step_description","")
        step.save()
        sub_step.save()
        status=200
        data['msg'] = u"步骤保存成功"
    except Exception,e:
        data['msg'] = msg if msg else u"步骤保存失败"
        error = traceback.format_exc()
        logger.error(error)
        print error
    return HttpResponse(json.dumps({
            "status":status,
            "result":data
    }, cls=LazyEncoder))

@login_required
@csrf_exempt
def job_start_now(request,job_id):
    '''
        start job now.
    '''
    status = 500
    data = {}
    user = request.user
    msg = ""
    try:
        job = _job.Job.objects.get(id=job_id)
        #TODO
        ''' 验证作业是否可以执行
                            文本步骤:文本内容
                            脚本步骤:版本，目标机器
                            分发文件：
                            拉取文件
        '''
        
        job_steps = _job.get_jobSteps_by_params(job=job,is_checked=True,is_delete=False).order_by('order')
        for job_step in job_steps:
            if job_step.step_type == enum_template.STEP_TYPE_PULL_FILE:
                sub_step = _job.get_jobStepPullFile_by_params(step=job_step)
                if not sub_step.pull_to or not sub_step.pull_to_ip or not sub_step.file_paths:
                    msg =  u'请补全文件拉取步骤【%s】必填信息'%job_step.name

            elif job_step.step_type == enum_template.STEP_TYPE_PUSH_FILE:
                sub_step = _job.get_jobStepPushFile_by_params(step=job_step)
                if not sub_step.push_to:
                    msg =  u'请补全文件分发步骤【%s】必填信息'%job_step.name

            elif job_step.step_type == enum_template.STEP_TYPE_SCRIPT:
                jobStepScript = _job.get_jobStepScript_by_params(step=job_step)
                if not jobStepScript.version:
                    msg =  u'脚本步骤【%s】未设置脚本版本'%job_step.name

            elif job_step.step_type == enum_template.STEP_TYPE_TEXT:
                job_step_text = _job.get_jobStepText_by_params(step=job_step)
                if not job_step_text.describe or not job_step_text.describe:
                    msg =  u'文本步骤【%s】未设置描述'%job_step.name

            if job_step.step_type in [enum_template.STEP_TYPE_PULL_FILE,enum_template.STEP_TYPE_PUSH_FILE,enum_template.STEP_TYPE_SCRIPT]:
                if not job_step.target and not job.target:
                    msg =  u'请设置脚本步骤【%s】目标机器或配置全局目标机器'%job_step.name

            if msg:
                data['msg'] = msg
                logger.debug("start check fail, job_id: {0}, step_id:{1}".format(job.id,job_step.id))
                return HttpResponse(json.dumps({
                        "status": status,
                        "result": data
                }))

        logger.debug("job param check ok, start handle job..")
        result = handle_job(job,user)
        status=result['status']
        data['history_id'] = result['result']['history_id']
    except:
        error = traceback.format_exc()
        logger.error(error)
        print error
        data['msg'] = u'执行作业出错'
    return HttpResponse(json.dumps({
        "status": status,
        "result": data
    }))

@login_required
@csrf_exempt
def full_settings_save(request, job_id):
    """
        save full settings of job.

    """
    user = request.user
    status = 500
    data = {}
    try:
        mode = request.POST.get("mode", None)
        account_id = request.POST.get("job_account", None)

        if mode == None or account_id == None:
            msg = u"invalid argument"
        else:
            account = _account.get_account_by_params(id=int(account_id))
            job = _job.get_job_by_params(id=job_id)

            ips_json = request.POST.get('full_settings_ips_hide',"")
            ip_set = get_input_ips(ips_json)
            job.target = json.dumps(list(ip_set))

            job.mode = mode
            job.account = account
            job.save()
            msg = "save success"
            status = 200
    except Exception as e:
        msg = "ops, error "
        print traceback.format_exc()
    data.update({
        "msg": msg
    })
    return HttpResponse(json.dumps({
        "status": status,
        "result": data
    }, cls=LazyEncoder))
    
@login_required
@csrf_exempt
@commit_on_success
def template_job_sync(request):
    '''
        template job sync
    '''
    sdicts = {}
    user = request.user
    code = 500

    if request.method == 'POST':
        try:
            template_id = request.POST.get('template_id',0)
            check_list = request.POST.getlist('check_list[]',[])
            template = _template.get_template_by_params(id=template_id)
            for job_id in check_list:
                if job_id:
                    job = _job.get_job_by_params(id=job_id)
                    templateSteps = _template.get_templateSteps_by_params(template=template)
                    for templateStep in templateSteps:
                        jobStep = _job.get_jobStep_by_params(job=job,template_step=templateStep)
                        step_type =  templateStep.step_type
                        #替换
                        if jobStep:
                            #脚本步骤
                            if step_type == enum_template.STEP_TYPE_SCRIPT:
                                templateStepScript = _template.get_templateStepScript_by_params(step=templateStep)
                                jobStepScript = _job.get_jobStepScript_by_params(step=jobStep)
                                if templateStepScript.version and jobStepScript.version and templateStepScript.version.script != jobStepScript.version.script:
                                    jobStepScript.version = templateStepScript.version
                                    jobStepScript.save()
                                if templateStepScript.version and not jobStepScript.version:
                                    jobStepScript.version=templateStepScript.version
                                    jobStepScript.save()
                            #拉取文件
                            elif step_type == enum_template.STEP_TYPE_PULL_FILE:
                                pass
                            #分发文件
                            elif step_type == enum_template.STEP_TYPE_PUSH_FILE:
                                pass
                            #文本步骤
                            elif step_type == enum_template.STEP_TYPE_TEXT:
                                templateStepText = _template.get_templateStepText_by_params(step=templateStep)
                                jobStepText = _job.get_jobStepText_by_params(step=jobStep)
                                jobStepText.describe = templateStepText.describe
                                jobStepText.save()
                            jobStep.name = templateStep.name
                            jobStep.describe = templateStep.describe
                            jobStep.order = templateStep.order
                            jobStep.is_delete = templateStep.is_delete
                            jobStep.save()
                        #新建
                        else:
                            jobStep = _job.create_jobStep_by_params(job=job,template_step=templateStep)
                            jobStep.name = templateStep.name
                            jobStep.describe = templateStep.describe
                            jobStep.step_type = templateStep.step_type
                            jobStep.order = templateStep.order
                            jobStep.is_setting = templateStep.is_setting
                            jobStep.account = templateStep.account
                            jobStep.target = templateStep.target
                            jobStep.is_checked = False
                            jobStep.is_delete = templateStep.is_delete
                            jobStep.save()
                            #脚本步骤
                            if step_type == enum_template.STEP_TYPE_SCRIPT:
                                sub_step = _template.get_templateStepScript_by_params(step=templateStep)
                                new_sub_step = _job.create_jobStepScript_by_params(step=jobStep)
                                new_sub_step.version=sub_step.version
                                new_sub_step.parameter = sub_step.parameter
                                new_sub_step.timeout = sub_step.timeout
                                new_sub_step.save()
                            #拉取文件
                            elif step_type == enum_template.STEP_TYPE_PULL_FILE:
                                sub_step = _template.get_templateStepPullFile_by_params(step=templateStep)
                                new_sub_step = _job.create_jobStepPullFile_by_params(step=jobStep)
                                new_sub_step.limit = sub_step.limit
                                new_sub_step.pull_to = sub_step.pull_to
                                new_sub_step.pull_to_ip = sub_step.pull_to_ip
                                new_sub_step.file_paths = sub_step.file_paths
                                new_sub_step.save()
                            #分发文件
                            elif step_type == enum_template.STEP_TYPE_PUSH_FILE:
                                sub_step = _template.get_templateStepPushFile_by_params(step=templateStep)
                                new_sub_step = _job.create_jobStepPushFile_by_params(step=jobStep)
                                new_sub_step.limit = sub_step.limit
                                new_sub_step.push_to = sub_step.push_to
                                new_sub_step.save()
                                
                                templateFileinfos = _template.get_templateFileInfos_by_params(step=templateStep)
                                if templateFileinfos:
                                    for templateFileinfo in templateFileinfos:
                                        jobFileInfo = _job.get_or_create_jobFileInfo_by_params(step=jobStep, remote_ip=templateFileinfo.remote_ip, \
                                                                                 push_account=templateFileinfo.push_account, location_type=templateFileinfo.location_type, \
                                                                                 remote_path=templateFileinfo.remote_path, record=templateFileinfo.record)[0]
                                        jobFileInfo.save()
                            #文本步骤
                            elif step_type == enum_template.STEP_TYPE_TEXT:
                                sub_step = _template.get_templateStepText_by_params(step=templateStep)
                                new_sub_step = _job.create_jobStepText_by_params(step=jobStep)
                                new_sub_step.describe = sub_step.describe
                                new_sub_step.save()
                                
                    job.is_sync = True
                    job.save()
                    
            code = 200
        except Exception,e:
            code = 500
            print traceback.format_exc()

    
        sdicts['status'] = code
        return HttpResponse(json.dumps(sdicts))

@login_required
@csrf_exempt
@commit_on_success
def job_add_v2(request):
    '''
        add job
    '''
    sdicts = {}
    user = request.user
    code = 500
    now = datetime.datetime.now()
    
    try:
        name = u'作业实例_%s_%s'%(user.username,datetime.datetime.strftime(now,'%Y%m%d%H%M%S'))
        
        template = _template.create_template_by_params(name=name)
        template.create_user = user
        template.update_user = user
        template.save()
        
        templateForm = EditTemplateForm(instance=template,user=request.user)
        code = 200
    except:
        error = traceback.format_exc()
        logger.error(error)
        print error
        code = 500
        sdicts['msg'] = u"添加实例失败！"
    
    accounts = _account.get_accounts_by_params(is_delete=False)
    account_id = template.account.id if template.account else ""
    accountForm = AccountForm()
    target_ips = json.loads(template.target) if template.target else []
    hide_ip_dict = build_hidden_ip_dict(target_ips)
    hide_ip_json = json.dumps(hide_ip_dict)
    
    ajax_url = "/md_manage/template_step/list_v2/{0}/".format(template.pk)
    template_file = "job_manage/job_view.html"
    html = render_to_string(template_file, locals())
    sdicts['status'] = code
    sdicts['template_id'] = template.id
    sdicts['template_name'] = template.name
    sdicts['html'] = html
    return HttpResponse(json.dumps(sdicts))

@login_required
@csrf_exempt
@commit_on_success
def job_view_v2(request):
    '''
        view job
    '''
    
    sdicts = {}
    user = request.user
    code = 500
    if request.method == 'POST':
        try:
            template_id = request.POST.get('template.id',0)
            template_name = request.POST.get('name')
            template_type = request.POST.get('template_type')
            work_type = request.POST.get('work_type')
            template_remarks = request.POST.get('remarks')
            check_list_post = request.POST.getlist('check_list[]',[u''])
            
            template = _template.get_template_by_params(id=template_id)
            templateStep_list = _template.get_templateSteps_by_params(template=template,is_delete=False).order_by('order')
            templateForm = EditTemplateForm(request.POST,instance=template,user=request.user)
            if not templateForm.is_valid():
                msg = u"form验证不通过"
                raise Exception,msg
            templates = _template.get_templates_by_params(create_user=user,name=template_name,is_delete=False).exclude(id=template.id)
            if templates:
                return HttpResponse(json.dumps({
                        "status":500,
                        "msg": u"实例名称已存在！"
                    }))
        
            template.name = template_name
            template.template_type = template_type
            template.work_type = work_type
            template.remarks = template_remarks
            template.update_user = user
            template.save()
            
            check_list_str = check_list_post[0]
            check_list = []
            if check_list_str:
                check_list = check_list_str.split(',')
            for templateStep in templateStep_list:
                step_type = templateStep.step_type
                if '%s'%templateStep.id in check_list:
                    templateStep.is_checked = True
                else:
                    templateStep.is_checked = False
                templateStep.save()
                
            code = 200
        except:
            error = traceback.format_exc()
            logger.error(error)
            print error
            code = 500
            sdicts['msg'] = u"保存实例失败！"
    else:
        template_id = request.GET.get('template_id',0)
        template = _template.get_template_by_params(id=template_id)
        if template:
            templateStep_list = _template.get_templateSteps_by_params(template=template,is_delete=False).order_by('order')
            templateForm = EditTemplateForm(instance=template,user=request.user)
            code = 200
        else:
            code = 500
            sdicts['msg'] = u"查看实例失败！"
    
    accounts = _account.get_accounts_by_params(is_delete=False)
    account_id = template.account.id if template.account else ""
    accountForm = AccountForm()
    target_ips = json.loads(template.target) if template.target else []
    hide_ip_dict = build_hidden_ip_dict(target_ips)
    hide_ip_json = json.dumps(hide_ip_dict)
    
#    ajax_url = "/md_manage/template_step/list_v2/{0}/".format(template.pk)
    template_file = "job_manage/job_view.html"
    html = render_to_string(template_file, locals())
    sdicts['status'] = code
    sdicts['template_id'] = template.id
    sdicts['template_name'] = template.name
    sdicts["work_type"] = template.work_type
    sdicts['html'] = html
    return HttpResponse(json.dumps(sdicts))

@login_required
@csrf_exempt
def job_delete_v2(request):
    '''
        delete template
    '''
    sdicts = {}
    template_id = request.POST.get('template_id',0)
    user = request.user
    template = _template.get_template_by_params(id=template_id)
    if template:
        template.is_delete = True
        template.update_user = user
        template.save()
        sdicts['result'] = 1
        sdicts['showMsg'] = _(u"删除成功")
    else:
        sdicts = {'result':0}
        sdicts['showMsg'] = _(u"删除失败")
    return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))

@login_required
@csrf_exempt
def job_copy_v2(request):
    '''
        copy version
    '''
    sdicts = {}
    user = request.user
    code = 500
    now = datetime.datetime.now()
    
    try:
        template_id = request.GET.get('template_id',0)
        template_copy = _template.get_template_by_params(id=template_id)
        templateStep_list_copy = _template.get_templateSteps_by_params(template=template_copy,is_delete=False).order_by("order")
        
        template_name = u'作业实例_%s_%s'%(user.username,datetime.datetime.strftime(now,'%Y%m%d%H%M%S'))
        template = _template.create_template_by_params()
        template.name = template_name
        
        template.template_type = template_copy.template_type
        template.work_type = template_copy.work_type
        template.remarks = template_copy.remarks
        template.create_user = user
        template.update_user = user
        template.mode = template_copy.mode
        template.account = template_copy.account
        template.target = template_copy.target
        template.save()
        
        for templateStep_copy in templateStep_list_copy:
            step_type = templateStep_copy.step_type  
            
            templateStep = _template.create_templateStep_by_params(template=template)
            templateStep.name = templateStep_copy.name
            templateStep.describe = templateStep_copy.describe
            templateStep.step_type = templateStep_copy.step_type
            templateStep.order = templateStep_copy.order
            templateStep.is_setting = templateStep_copy.is_setting
            templateStep.account = templateStep_copy.account
            templateStep.target = templateStep_copy.target
            templateStep.is_checked = templateStep_copy.is_checked
            templateStep.is_delete = templateStep_copy.is_delete
            templateStep.save()
            #脚本步骤
            if step_type == enum_template.STEP_TYPE_SCRIPT:
                sub_step = _template.get_templateStepScript_by_params(step=templateStep_copy)
                new_sub_step = _template.create_templateStepScript_by_params(step=templateStep)
                new_sub_step.version=sub_step.version
                new_sub_step.parameter = sub_step.parameter
                new_sub_step.timeout = sub_step.timeout
                new_sub_step.save()
            #拉取文件
            elif step_type == enum_template.STEP_TYPE_PULL_FILE:
                sub_step = _template.get_templateStepPullFile_by_params(step=templateStep_copy)
                new_sub_step = _template.create_templateStepPullFile_by_params(step=templateStep)
                new_sub_step.limit = sub_step.limit
                new_sub_step.pull_to = sub_step.pull_to
                new_sub_step.pull_to_ip = sub_step.pull_to_ip
                new_sub_step.file_paths = sub_step.file_paths
                new_sub_step.save()
            #分发文件
            elif step_type == enum_template.STEP_TYPE_PUSH_FILE:
                sub_step = _template.get_templateStepPushFile_by_params(step=templateStep_copy)
                new_sub_step = _template.create_templateStepPushFile_by_params(step=templateStep)
                new_sub_step.limit = sub_step.limit
                new_sub_step.push_to = sub_step.push_to
                new_sub_step.save()
            #文本步骤
            elif step_type == enum_template.STEP_TYPE_TEXT:
                sub_step = _template.get_templateStepText_by_params(step=templateStep_copy)
                new_sub_step = _template.create_templateStepText_by_params(step=templateStep)
                new_sub_step.describe = sub_step.describe
                new_sub_step.save()
        
        templateStep_list = _template.get_templateSteps_by_params(template=template,is_delete=False).order_by('order')
        code = 200
    except:
        error = traceback.format_exc()
        logger.error(error)
        print error
        code = 500
        sdicts['msg'] = u"复制实例失败！"
    
    templateForm = EditTemplateForm(instance=template,user=request.user)
    
    accounts = _account.get_accounts_by_params(is_delete=False)
    account_id = template.account.id if template.account else ""
    accountForm = AccountForm()
    target_ips = json.loads(template.target) if template.target else []
    hide_ip_dict = build_hidden_ip_dict(target_ips)
    hide_ip_json = json.dumps(hide_ip_dict)
    
#    ajax_url = "/md_manage/template_step/list_v2/{0}/".format(template.pk)
    template_file = "job_manage/job_view.html"
    html = render_to_string(template_file, locals())
    sdicts['status'] = code
    sdicts['template_id'] = template.id
    sdicts['html'] = html
    sdicts['work_type'] = template.work_type
    return HttpResponse(json.dumps(sdicts))

@login_required
@csrf_exempt
def job_start_now_v2(request,template_id):
    '''
        start job now.
    '''
    status = 500
    data = {}
    user = request.user
    msg = ""
    
    #copy job from template
    template = _template.get_template_by_params(id=template_id)
    job = job_sync_v2(template)
    
    try:
        ''' 验证作业是否可以执行
                            文本步骤:文本内容
                            脚本步骤:版本，目标机器
                            分发文件：
                            拉取文件
        '''
        
        job_steps = _job.get_jobSteps_by_params(job=job,is_checked=True,is_delete=False).order_by('order')
        if not job_steps:
            msg =  u'请添加作业步骤后执行'
        for job_step in job_steps:
            if job_step.step_type == enum_template.STEP_TYPE_PULL_FILE:
                sub_step = _job.get_jobStepPullFile_by_params(step=job_step)
                if not sub_step.pull_to or not sub_step.pull_to_ip or not sub_step.file_paths:
                    msg =  u'请补全文件拉取步骤【%s】必填信息'%job_step.name

            elif job_step.step_type == enum_template.STEP_TYPE_PUSH_FILE:
                sub_step = _job.get_jobStepPushFile_by_params(step=job_step)
                if not sub_step.push_to:
                    msg =  u'请补全文件分发步骤【%s】必填信息'%job_step.name

            elif job_step.step_type == enum_template.STEP_TYPE_SCRIPT:
                jobStepScript = _job.get_jobStepScript_by_params(step=job_step)
                if not jobStepScript.version:
                    msg =  u'脚本步骤【%s】未设置脚本版本'%job_step.name

            elif job_step.step_type == enum_template.STEP_TYPE_TEXT:
                job_step_text = _job.get_jobStepText_by_params(step=job_step)
                if not job_step_text.describe or not job_step_text.describe:
                    msg =  u'文本步骤【%s】未设置描述'%job_step.name

            if job_step.step_type in [enum_template.STEP_TYPE_PULL_FILE,enum_template.STEP_TYPE_PUSH_FILE,enum_template.STEP_TYPE_SCRIPT]:
                if not job_step.target and not job.target:
                    msg =  u'请设置脚本步骤【%s】目标机器或配置全局目标机器'%job_step.name

        if msg:
            data['msg'] = msg
            logger.debug("start check fail, job_id: {0}, step_id:{1}".format(job.id,job_step.id))
            return HttpResponse(json.dumps({
                    "status": status,
                    "result": data
            }))

        logger.debug("job param check ok, start handle job..")
        result = handle_job(job,user)
        status=result['status']
        data['history_id'] = result['result']['history_id']
    except:
        error = traceback.format_exc()
        logger.error(error)
        print error
        data['msg'] = u'执行作业出错'
    return HttpResponse(json.dumps({
        "status": status,
        "result": data
    }))
    
def job_sync_v2(template):
    job = _job.get_or_create_job_by_params(template=template)[0]
    job.name = template.name
    job.remarks = template.remarks
    job.create_user = template.create_user
    job.update_user = template.update_user
    job.created = template.created
    job.updated = template.updated
    job.mode = template.mode
    job.account = template.account
    job.target = template.target
    job.is_delete = template.is_delete
    job.is_sync = True
    
    templateSteps = _template.get_templateSteps_by_params(template=template)
    for templateStep in templateSteps:
        jobStep = _job.get_jobStep_by_params(job=job,template_step=templateStep)
        step_type =  templateStep.step_type
        #替换
        if jobStep:
            #脚本步骤
            if step_type == enum_template.STEP_TYPE_SCRIPT:
                templateStepScript = _template.get_templateStepScript_by_params(step=templateStep)
                jobStepScript = _job.get_jobStepScript_by_params(step=jobStep)
                jobStepScript.version = templateStepScript.version
                jobStepScript.parameter = templateStepScript.parameter
                jobStepScript.timeout = templateStepScript.timeout
                jobStepScript.save()
            #拉取文件
            elif step_type == enum_template.STEP_TYPE_PULL_FILE:
                templateStepPullFile = _template.get_templateStepPullFile_by_params(step=templateStep)
                jobStepPullFile = _job.get_jobStepPullFile_by_params(step=jobStep)
                jobStepPullFile.limit = templateStepPullFile.limit
                jobStepPullFile.pull_to = templateStepPullFile.pull_to
                jobStepPullFile.pull_to_ip = templateStepPullFile.pull_to_ip
                jobStepPullFile.file_paths = templateStepPullFile.file_paths
                jobStepPullFile.save()
            #分发文件
            elif step_type == enum_template.STEP_TYPE_PUSH_FILE:
                templateStepPushFile = _template.get_templateStepPushFile_by_params(step=templateStep)
                jobStepPushFile = _job.get_jobStepPushFile_by_params(step=jobStep)
                jobStepPushFile.limit = templateStepPushFile.limit
                jobStepPushFile.push_to = templateStepPushFile.push_to
                jobStepPushFile.save()

                ### 更新文件信息
                _job.get_jobFileInfos_by_params(step=jobStep).delete()
                templateFileinfos = _template.get_templateFileInfos_by_params(step=templateStep)
                for templateFileinfo in templateFileinfos:
                        jobFileInfo = _job.get_or_create_jobFileInfo_by_params(step=jobStep, remote_ip=templateFileinfo.remote_ip,
                                                                 push_account=templateFileinfo.push_account, location_type=templateFileinfo.location_type,
                                                                 remote_path=templateFileinfo.remote_path, record=templateFileinfo.record)[0]
                        jobFileInfo.save()

            #文本步骤
            elif step_type == enum_template.STEP_TYPE_TEXT:
                templateStepText = _template.get_templateStepText_by_params(step=templateStep)
                jobStepText = _job.get_jobStepText_by_params(step=jobStep)
                jobStepText.describe = templateStepText.describe
                jobStepText.save()
            jobStep.name = templateStep.name
            jobStep.describe = templateStep.describe
            jobStep.step_type = templateStep.step_type
            jobStep.order = templateStep.order
            jobStep.is_setting = templateStep.is_setting
            jobStep.account = templateStep.account
            jobStep.target = templateStep.target
            jobStep.is_checked = templateStep.is_checked
            jobStep.is_delete = templateStep.is_delete
            jobStep.save()
        #新建
        else:
            jobStep = _job.create_jobStep_by_params(job=job,template_step=templateStep)
            jobStep.name = templateStep.name
            jobStep.describe = templateStep.describe
            jobStep.step_type = templateStep.step_type
            jobStep.order = templateStep.order
            jobStep.is_setting = templateStep.is_setting
            jobStep.account = templateStep.account
            jobStep.target = templateStep.target
            jobStep.is_checked = templateStep.is_checked
            jobStep.is_delete = templateStep.is_delete
            jobStep.save()
            #脚本步骤
            if step_type == enum_template.STEP_TYPE_SCRIPT:
                sub_step = _template.get_templateStepScript_by_params(step=templateStep)
                new_sub_step = _job.create_jobStepScript_by_params(step=jobStep)
                new_sub_step.version=sub_step.version
                new_sub_step.parameter = sub_step.parameter
                new_sub_step.timeout = sub_step.timeout
                new_sub_step.save()
            #拉取文件
            elif step_type == enum_template.STEP_TYPE_PULL_FILE:
                sub_step = _template.get_templateStepPullFile_by_params(step=templateStep)
                new_sub_step = _job.create_jobStepPullFile_by_params(step=jobStep)
                new_sub_step.limit = sub_step.limit
                new_sub_step.pull_to = sub_step.pull_to
                new_sub_step.pull_to_ip = sub_step.pull_to_ip
                new_sub_step.file_paths = sub_step.file_paths
                new_sub_step.save()
            #分发文件
            elif step_type == enum_template.STEP_TYPE_PUSH_FILE:
                sub_step = _template.get_templateStepPushFile_by_params(step=templateStep)
                new_sub_step = _job.create_jobStepPushFile_by_params(step=jobStep)
                new_sub_step.limit = sub_step.limit
                new_sub_step.push_to = sub_step.push_to
                new_sub_step.save()
                
                templateFileinfos = _template.get_templateFileInfos_by_params(step=templateStep)
                if templateFileinfos:
                    for templateFileinfo in templateFileinfos:
                        jobFileInfo = _job.get_or_create_jobFileInfo_by_params(step=jobStep, remote_ip=templateFileinfo.remote_ip, \
                                                                 push_account=templateFileinfo.push_account, location_type=templateFileinfo.location_type, \
                                                                 remote_path=templateFileinfo.remote_path, record=templateFileinfo.record)[0]
                        jobFileInfo.save()
            #文本步骤
            elif step_type == enum_template.STEP_TYPE_TEXT:
                sub_step = _template.get_templateStepText_by_params(step=templateStep)
                new_sub_step = _job.create_jobStepText_by_params(step=jobStep)
                new_sub_step.describe = sub_step.describe
                new_sub_step.save()
                
    job.is_sync = True
    job.save()
    return job
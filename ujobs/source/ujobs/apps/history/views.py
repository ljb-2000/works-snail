#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Created on 2015-09-09

@author: wx
'''

import os, sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
sys.path.insert(0, os.path.abspath(os.curdir))

from utils.decorator import render_to, login_required
#from django.db.transaction import commit_on_success
from django.views.decorators.csrf import csrf_exempt
from service import _history
from utils.utils import _handle_job
import threading,json, traceback, datetime
from django.http import HttpResponse
from enums import enum_history
from utils.utils import ThreadInfo
#from utils.utils import JobThread

def thread_terminate(thread):
    import platform, ctypes
    system = platform.system()
    ident = thread.ident
    if 'Windows' in system:
        pthread = ctypes.cdll.LoadLibrary("Kernel32.dll")
        pthread.TerminateThread(ctypes.c_ulong(ident))
    elif 'Linux' in system:
        pthread = ctypes.cdll.LoadLibrary("libpthread.so.0")
        pthread.pthread_cancel(ctypes.c_ulong(ident))

@login_required
@csrf_exempt
def history_step_restart(request):
    history_step_id = request.POST.get('history_step_id',0)
    history_step = _history.get_historyStep_by_params(id=history_step_id)
    
    if history_step:
        history = history_step.history
        history.start_time = datetime.datetime.now()
        history.end_time = None
        history.delta_time = None
        history.status = enum_history.STATUS_PROCESSING
        history.save()
        
        thread_name = 'Thread-history-%s'%history.id
        thread = ThreadInfo.data.get(thread_name)
        if thread and thread.isAlive():
            try:
#                thread.terminate()
                thread_terminate(thread)
                del ThreadInfo.data[thread_name]
            except Exception,e:
                print e
            
        history_job_steps = _history.get_historySteps_by_params(history=history).order_by('order')
        for history_step in history_job_steps:
            history_step.start_time = None
            history_step.end_time = None
            history_step.delta_time = None
            history_step.result = enum_history.RESULT_NOT_START
            history_step.total_ips = []
            history_step.abnormal_ips = []
            history_step.fail_ips = []
            history_step.success_ips = []
            history_step.save()
        
        thread = threading.Thread(target=_handle_job,args=(history.id,0,''))
#        thread = JobThread(history.id,0,'')
        thread_name = 'Thread-history-%s'%history.id
        thread.setName(thread_name)
        ThreadInfo.data['%s'%thread_name] = thread
        thread.start()
    
    return HttpResponse(json.dumps({}))

@login_required
@csrf_exempt
def history_step_stop(request):
    history_step_id = request.POST.get('history_step_id',0)
    history_step = _history.get_historyStep_by_params(id=history_step_id)
    
    if history_step:
        history = history_step.history
        history_job_steps = _history.get_historySteps_by_params(history=history).order_by('order')
        history_step = _history.get_historyStep_by_params(id=history_step_id)
        list_slice = list(history_job_steps).index(history_step)
        history_job_steps_new = history_job_steps[list_slice:]
        
        thread_name = 'Thread-history-%s'%history.id
        thread = ThreadInfo.data.get(thread_name)
        if thread and thread.isAlive():
            thread_terminate(thread)
            del ThreadInfo.data[thread_name]
        
        for history_step in history_job_steps_new:
            history_step.start_time = None
            history_step.end_time = None
            history_step.delta_time = None
            history_step.total_ips = []
            history_step.abnormal_ips = []
            history_step.fail_ips = []
            history_step.success_ips = []
            history_step.result = enum_history.RESULT_MANUAL_STOP
            history_step.save()
        
        history.end_time = datetime.datetime.now()
        history.status = enum_history.STATUS_SUCCESS
        history.delta_time = (history.end_time - history.start_time).seconds
        history.save()
    
    return HttpResponse(json.dumps({}))

@login_required
@csrf_exempt
def history_step_execute(request):
    history_step_id = request.POST.get('history_step_id',0)
    history_step = _history.get_historyStep_by_params(id=history_step_id)
    history_step.start_time = None
    history_step.end_time = None
    history_step.delta_time = None
#    history_step.result = enum_history.RESULT_NOT_START
    history_step.total_ips = []
    history_step.abnormal_ips = []
    history_step.fail_ips = []
    history_step.success_ips = []
    history_step.save()
    
    history = history_step.history
    history.end_time = None
    history.delta_time = None
    history.status = enum_history.STATUS_PROCESSING
    history.save()
    
    thread_name = 'Thread-history-%s'%history.id
    thread = ThreadInfo.data.get(thread_name)
    if thread and thread.isAlive():
        thread_terminate(thread)
        del ThreadInfo.data[thread_name]
    
    if history_step:
        thread = threading.Thread(target=_handle_job,args=(history.id,history_step.id,'execute'))
        thread_name = 'Thread-history-%s'%history.id
        thread.setName(thread_name)
        ThreadInfo.data['%s'%thread_name] = thread
        thread.start()
        
#        if history.mode == enum_template.TEMPLATE_MODE_AUTO:
#            history_job_steps = _history.get_historySteps_by_params(history=history).order_by('order')
#            list_slice = list(history_job_steps).index(history_step)
#            history_job_steps_new = history_job_steps[list_slice:]
#            _handle_job_auto(history,history_job_steps_new)
#
#        if history.mode == enum_template.TEMPLATE_MODE_MANNUAL:
#            _handle_job_mannual(history,history_step)
#                    
#        if history.mode == enum_template.TEMPLATE_MODE_MIX:
#            _handle_job_mix(history,history_job_steps_new)
        
    return HttpResponse(json.dumps({}))

@login_required
@csrf_exempt
def history_step_skip(request):
    history_step_id = request.POST.get('history_step_id',0)
    history_step = _history.get_historyStep_by_params(id=history_step_id)
    
    if history_step:
        history = history_step.history
        history_step = _history.get_historyStep_by_params(id=history_step_id)
#        history_step.start_time = None
#        history_step.end_time = None
#        history_step.delta_time = None
        history_step.result = enum_history.RESULT_SKIP
#        history_step.total_ips = []
#        history_step.abnormal_ips = []
#        history_step.fail_ips = []
#        history_step.success_ips = []
        history_step.save()
        
        thread_name = 'Thread-history-%s'%history.id
        thread = ThreadInfo.data.get(thread_name)
        if  thread and thread.isAlive():
            thread_terminate(thread)
            del ThreadInfo.data[thread_name]
        
        history_job_steps = _history.get_historySteps_by_params(history=history).order_by('-order')
        if history_step == history_job_steps[0]:
            history.end_time = datetime.datetime.now()
            history.status = enum_history.STATUS_SUCCESS
            history.delta_time = (history.end_time - history.start_time).seconds
            history.save()
        else:
            history.status = enum_history.STATUS_PROCESSING
            history.save()
            index = list(history_job_steps).index(history_step)
            history_step_next = history_job_steps[index-1]
            thread = threading.Thread(target=_handle_job,args=(history.id,history_step_next.id,''))
            thread_name = 'Thread-history-%s'%history.id
            thread.setName(thread_name)
            ThreadInfo.data['%s'%thread_name] = thread
            thread.start()
            
#        if history.mode == enum_template.TEMPLATE_MODE_AUTO:
#            history_job_steps = _history.get_historySteps_by_params(history=history).order_by('-order')
#            if history_step == history_job_steps[0]:
#                history.end_time = datetime.datetime.now()
#                history.status = enum_history.STATUS_SUCCESS
#                history.delta_time = (history.end_time - history.start_time).seconds
#                history.save()
#            else:
#                history_job_steps = _history.get_historySteps_by_params(history=history).order_by('order')
#                list_slice = list(history_job_steps).index(history_step)+1
#                history_job_steps_new = history_job_steps[list_slice:]
#                _handle_job_auto(history,history_job_steps_new)

#        if history.mode == enum_template.TEMPLATE_MODE_MANNUAL:
#            history_job_steps = _history.get_historySteps_by_params(history=history).order_by('-order')
#            if history_step == history_job_steps[0]:
#                history.end_time = datetime.datetime.now()
#                history.status = enum_history.STATUS_SUCCESS
#                history.delta_time = (history.end_time - history.start_time).seconds
#                history.save()
#            else:
#                index = list(history_job_steps).index(history_step)
#                history_step_next = history_job_steps[index-1]
#                history_step_next.result = enum_history.RESULT_WAIT_USER
#                history_step_next.save()
#                    
#        if history.mode == enum_template.TEMPLATE_MODE_MIX:
#            history_job_steps = _history.get_historySteps_by_params(history=history).order_by('order')
#            list_slice = list(history_job_steps).index(history_step)+1
#            history_job_steps_new = history_job_steps[list_slice:]
#            _handle_job_mix(history,history_job_steps_new)
        
    return HttpResponse(json.dumps({}))
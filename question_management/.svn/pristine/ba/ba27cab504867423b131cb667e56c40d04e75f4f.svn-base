#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

import settings
from utils.decorator import render_to, login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.transaction import commit_on_success
from django.shortcuts import HttpResponse
from django.template.loader import render_to_string
import json
import datetime
from ftplib import FTP
import logging
import traceback
from service import _question
from django.core.paginator import Paginator
from enums import enum_question
from question_management.views import get_product_add

logger = logging.getLogger('logger')

@login_required
@csrf_exempt
def question_list(request):
    user = request.user
    product_add,user_type = get_product_add(user)
    
    product_id = request.GET.get('product_id')
    qtime_from = request.GET.get('qtime_from','').strip()
    qtime_to = request.GET.get('qtime_to','').strip()
    created_from = request.GET.get('created_from','').strip()
    created_to = request.GET.get('created_to','').strip()
    status = request.GET.get('status')
    level = request.GET.get('level')
    qtype = request.GET.get('qtype')
    title = request.GET.get('title','').strip()
    describe = request.GET.get('describe','').strip()
    create_user = request.GET.get('create_user','').strip()
    
    iDisplayLength = int(request.GET.get('iDisplayLength'))
    iDisplayStart = int(request.GET.get('iDisplayStart'))
    sEcho = int(request.GET.get('sEcho'))
    iSortCol_0 = int(request.GET.get('iSortCol_0'))
    sSortDir_0 = request.GET.get('sSortDir_0')
    order_list = ['id', 'product__name', 'title', 'create_user__username', 'status','level', 'qtype', 'qtime', 'created', None]
    order_item = order_list[iSortCol_0]
    
    questions = _question.get_questions_by_params()

    if product_id:
        product = _question.get_product_by_params(id=product_id)
        questions = questions.filter(product=product)
        
    one_day = datetime.timedelta(days=1)
    if qtime_from:
        questions = questions.filter(qtime__gte = qtime_from)
    if qtime_to:
        qtime_to = datetime.datetime.strptime(qtime_to,'%Y-%m-%d %H:%M')
        questions = questions.filter(qtime__lte = (qtime_to+one_day))
    
    if created_from:
        questions = questions.filter(created__gte = created_from)
    if created_to:
        created_to = datetime.datetime.strptime(created_to,'%Y-%m-%d %H:%M')
        questions = questions.filter(created__lte = (created_to+one_day))
    
    if status:
        questions = questions.filter(status = status)
    if level:
        questions = questions.filter(level = level)
    if qtype:
        questions = questions.filter(qtype = qtype)
    if title:
        questions = questions.filter(title__icontains = title)
    if describe:
        questions = questions.filter(describe__icontains = describe)
    if create_user:
        questions = questions.filter(create_user__username__icontains = create_user)
        
    if order_item:
        if sSortDir_0 == "desc":
            order_item = '-%s' % order_item
        questions = questions.order_by(order_item)
    else:
        questions = questions.order_by('-id')
    
    #第一个参数表示需要分页的对象，可为list、tuple、QuerySet，只要它有count()或者__len__()函数
    #第二个参数为每页显示记录数
    p = Paginator(questions, iDisplayLength)
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
        qtime = datetime.datetime.strftime(obj.qtime,'%Y-%m-%d %H:%M:%S') if obj.qtime else ""
        created = datetime.datetime.strftime(obj.created,'%Y-%m-%d %H:%M:%S') if obj.created else ""
        
        if user_type == 2 and obj.product.name in product_add:
            operation = u'<a href="javascript:void(0);" onclick="question_edit(%s);" >跟进</a>'%obj.id
        else:
            operation = u'<a href="javascript:void(0);" onclick="question_view(%s);" >查看</a>'%obj.id
        data = [obj.id, obj.product.name, obj.title, obj.create_user.username, obj.get_status_display(), obj.get_level_display(), obj.get_qtype_display(), qtime, created, operation]
        sdicts["aaData"].append(data)
    return HttpResponse(json.dumps(sdicts, ensure_ascii=False))

@csrf_exempt
@login_required
def add(request):
    user = request.user
    sdicts = {}
    sdicts["result"] = 0
    
    product_name = request.POST.get('product_name','').strip()
    qtime = request.POST.get('qtime','').strip()
    status = request.POST.get('status')
    level = request.POST.get('level')
    qtype = request.POST.get('qtype')
    title = request.POST.get('title','').strip()
    describe = request.POST.get('describe','').strip()
    reason = request.POST.get('reason','').strip()
    solution = request.POST.get('solution','').strip()
    
    try:
        product = _question.get_or_create_product_by_params(name=product_name)[0]
        question = _question.create_question_by_params(product=product)
        question.qtime = qtime
        question.status = status
        question.level = level
        question.qtype = qtype
        question.title = title
        question.describe = describe
        question.reason = reason
        question.solution = solution
        question.create_user = user
        question.save()
        
        sdicts["result"] = 1
    except Exception,e:
        print e
        
    return HttpResponse(json.dumps(sdicts, ensure_ascii=False))

@csrf_exempt
@login_required
def edit(request):
    sdicts = {}
    user = request.user
    sdicts["result"] = 0
    
    if request.method == 'POST':
        question_id = request.POST.get('question_id',0)
        product_name = request.POST.get('product_name','').strip()
        qtime = request.POST.get('qtime','').strip()
        status = request.POST.get('status')
        level = request.POST.get('level')
        qtype = request.POST.get('qtype')
        title = request.POST.get('title','').strip()
        describe = request.POST.get('describe','').strip()
        reason = request.POST.get('reason','').strip()
        solution = request.POST.get('solution','').strip()
            
        try:
            product = _question.get_product_by_params(name=product_name)
            question = _question.get_question_by_params(id=question_id)
            question.product = product
            question.qtime = qtime
            question.status = status
            question.level = level
            question.qtype = qtype
            question.title = title
            question.describe = describe
            question.reason = reason
            question.solution = solution
            question.create_user = user
            question.save()
            
            sdicts["result"] = 1
        except Exception,e:
            print e
    
        return HttpResponse(json.dumps(sdicts))
    else:
        try:
            question_id = request.GET.get('question_id',0)
            question = _question.get_question_by_params(id=question_id)
            product_add,user_type = get_product_add(user)
            
            code = 200
        except Exception,e:
            code = 500
        
        template_file = "question/edit.html"
        html = render_to_string(template_file, locals())
        sdicts['status'] = code
        sdicts['html'] = html
        return HttpResponse(json.dumps(sdicts))

@csrf_exempt
@login_required
def view(request):
    sdicts = {}
    user = request.user
    sdicts["result"] = 0
    
    try:
        question_id = request.GET.get('question_id',0)
        question = _question.get_question_by_params(id=question_id)
        
        code = 200
    except Exception,e:
        code = 500
    
    template_file = "question/view.html"
    html = render_to_string(template_file, locals())
    sdicts['status'] = code
    sdicts['html'] = html
    return HttpResponse(json.dumps(sdicts))

@csrf_exempt
@login_required
def ajax_get_type_num(request):
    sdicts = {}
    sdicts["result"] = 0
    
    TYPE_1_num = _question.get_questions_by_params(status=enum_question.STATUS_OPEN, qtype=enum_question.TYPE_1).count()
    TYPE_2_num = _question.get_questions_by_params(status=enum_question.STATUS_OPEN, qtype=enum_question.TYPE_2).count()
    TYPE_3_num = _question.get_questions_by_params(status=enum_question.STATUS_OPEN, qtype=enum_question.TYPE_3).count()
    TYPE_4_num = _question.get_questions_by_params(status=enum_question.STATUS_OPEN, qtype=enum_question.TYPE_4).count()
    sdicts["data"] = [[enum_question.QUESTION_TYPE_CHOICES[0][1], TYPE_1_num],
                      [enum_question.QUESTION_TYPE_CHOICES[1][1], TYPE_2_num],
                      [enum_question.QUESTION_TYPE_CHOICES[2][1], TYPE_3_num],
                      [enum_question.QUESTION_TYPE_CHOICES[3][1], TYPE_4_num]]
    sdicts["result"] = 1
    return HttpResponse(json.dumps(sdicts, ensure_ascii=False))

@csrf_exempt
@login_required
def ajax_get_level_num(request):
    sdicts = {}
    sdicts["result"] = 0
    
    LEVEL_1_num = _question.get_questions_by_params(status=enum_question.STATUS_OPEN, level=enum_question.LEVEL_CRITICAL).count()
    LEVEL_2_num = _question.get_questions_by_params(status=enum_question.STATUS_OPEN, level=enum_question.LEVEL_NORMAL).count()
    LEVEL_3_num = _question.get_questions_by_params(status=enum_question.STATUS_OPEN, level=enum_question.LEVEL_SLIGHT).count()
    
    sdicts["data"] = [[enum_question.QUESTION_LEVEL_CHOICES[0][1], LEVEL_1_num],
                  [enum_question.QUESTION_LEVEL_CHOICES[1][1], LEVEL_2_num],
                  [enum_question.QUESTION_LEVEL_CHOICES[2][1], LEVEL_3_num]]
    sdicts["result"] = 1
    return HttpResponse(json.dumps(sdicts, ensure_ascii=False))

@csrf_exempt
@login_required
def ajax_get_product_num(request):
    sdicts = {}
    sdicts["result"] = 0
    
    product_num_list = []
    product_list = _question.get_products_by_params()
    for product in product_list:
        product_num = _question.get_questions_by_params(status=enum_question.STATUS_OPEN, product=product).count()
        product_num_list.append((product_num, product.name))
    
    product_num_list.sort(reverse=True)
    sdicts["data"] = product_num_list
    sdicts["result"] = 1
    return HttpResponse(json.dumps(sdicts, ensure_ascii=False))

@csrf_exempt
@login_required
def ajax_get_question_title(request):
    sdicts = {}
    sdicts["result"] = 0
    
    title_list = []
    title = request.GET.get('title','')
    if title:
        questions = _question.get_questions_by_params(title__icontains=title)
        title_list = list(set([question.title for question in questions ])) if questions else []
    sdicts["title_list"] = title_list
    sdicts["result"] = 1
    return HttpResponse(json.dumps(sdicts, ensure_ascii=False))


@csrf_exempt
@login_required
def ajax_get_question_describe(request):
    sdicts = {}
    sdicts["result"] = 0
    
    describe_list = []
    
    describe = request.GET.get('describe','')
    if describe:
        questions = _question.get_questions_by_params(describe__icontains=describe)
        describe_list = list(set([question.describe for question in questions ])) if questions else []
    sdicts["describe_list"] = describe_list
    sdicts["result"] = 1
    return HttpResponse(json.dumps(sdicts, ensure_ascii=False))

@csrf_exempt
@login_required
def ajax_get_summarize(request):
    sdicts = {}
    sdicts["result"] = 0
    
    today = datetime.datetime.today()
    total = _question.get_questions_by_params().count()
    close_num = _question.get_questions_by_params(status=enum_question.STATUS_CLOSE).count()
    open_num = total-close_num
    
    sdicts["username"] = request.user.username
    sdicts["year"] = today.year
    sdicts["month"] = today.month
    sdicts["day"] = today.day
    sdicts["total"] = total
    sdicts["open_num"] = open_num
    sdicts["close_num"] = close_num
    sdicts["result"] = 1
    return HttpResponse(json.dumps(sdicts, ensure_ascii=False))
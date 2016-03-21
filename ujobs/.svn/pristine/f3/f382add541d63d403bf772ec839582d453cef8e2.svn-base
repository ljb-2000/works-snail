#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 2015-5-22

@author: wx
'''

import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from utils.decorator import render_to, login_required
from django.db.transaction import commit_on_success
from django.views.decorators.csrf import csrf_exempt
from service import _account, _script
from django.http import HttpResponse
import json, traceback
from django.template.loader import render_to_string
from apps.accounts.forms import AccountForm
from utils.ctranslate import LazyEncoder
import hashlib
from enums import enum_account

@login_required
@csrf_exempt
def account_edit(request, account_id):
    '''
        edit account
    '''
    user = request.user
    account = _account.get_account_by_params(id=account_id)
    create_user = account.create_user
    sdicts = {'result':0}
    if request.method == 'POST':
        accountForm = AccountForm(request.POST, instance=account)
        if accountForm.is_valid():
            ac=accountForm.save(commit=False) 
            ac.password=hashlib.sha1(accountForm.cleaned_data['password']).hexdigest()
            ac.create_user = create_user
            ac.update_user = user
            ac.save() 
            accountForm.save_m2m()
            sdicts['result'] = 1
            sdicts['showMsg'] = _(u"修改成功")
    else:
        accountForm = AccountForm(instance=account)
        
    template_file = "account/edit.html"
    html = render_to_string(template_file, locals())
    sdicts['html'] = html
    return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))

@login_required
@csrf_exempt
@commit_on_success
def account_del(request, account_id):
    '''
        delete account
    '''
    user = request.user
    account = _account.get_account_by_params(id=account_id)
    sdicts = {'result':0}
    if request.method == 'POST':
        account.is_delete = True
        account.update_user = user
        account.save()
        sdicts['result'] = 1
        sdicts['showMsg'] = _(u"删除成功")
    table_fields = [u'账户别名', u'开发商', u'账户名称', u'创建时间', u'最后修改时间', u'最后修改人', u'操作']
    ajax_url = u'/account/list/' 
    template_file = "account/contentDiv.html"
    html = render_to_string(template_file, locals())
    sdicts['html'] = html
    return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))

@login_required
@csrf_exempt
@commit_on_success
def ajax_add_account(request):
    user = request.user
    method = request.method
    sdicts = {'result':0}
    accountForm = AccountForm()

    if method == 'POST':
        accountForm = AccountForm(request.POST)
        if accountForm.is_valid():
            account=accountForm.save(commit=False) 
            account.password=hashlib.sha1(accountForm.cleaned_data['password']).hexdigest() 
            account.create_user = user
            account.update_user = user
            account.save() 
            accountForm.save_m2m()
            sdicts['result'] = 1
            
    template_file = "account/account_modal.html"
    html = render_to_string(template_file, locals())
    sdicts['html'] = html
    return HttpResponse(json.dumps(sdicts, cls=LazyEncoder))

@login_required
@csrf_exempt
def get_account_list(request):
    """
        获取用户列表
    """
    user = request.user
    status = 500
    data = {}
    try:
        accounts = _account.get_accounts_by_params(is_delete=False,create_user=user)
        data.update({
            'accounts':[{"a_id":account.id,"a_name":u'%s&nbsp;&nbsp;账号:%s&nbsp;&nbsp;创建人:%s'%(account.name,account.name_abbr,account.create_user)} for account in accounts]
        })
        status = 200
    except:
        data['msg'] = u"账户列表更新失败"
        error = traceback.format_exc()
        print error
    return HttpResponse(json.dumps({
        'status':status,
        'result':data
    }, cls=LazyEncoder))
    
@login_required
@csrf_exempt
def get_account_list_v2(request):
    """
        获取授权用户列表
    """
    user = request.user
    status = 500
    data = {}
    try:
        perms = _account.get_perms_by_params(to_user=user, is_delete=False, ptype=enum_account.PERM_PTYPE_SCRIPT)
        scripts = _script.Script.objects.filter(Q(create_user=user)|Q(pk__in=[perm.object_id for perm in perms]),
                                                is_delete=False,is_once=False)
        
        scrip_id_list = [script.id for script in scripts]
        user_set = set()
        user_set.add(user)
        accounts_perm = _account.get_perms_by_params(object_id__in=scrip_id_list, is_delete=False)
        for account_perm in accounts_perm:
            user_set.add(account_perm.create_user)
            user_set.add(account_perm.to_user)
        accounts = _account.get_accounts_by_params(is_delete=False,create_user__in=list(user_set))
        
        data.update({
            'accounts':[{"a_id":account.id,"a_name":u'%s&nbsp;&nbsp;账号:%s&nbsp;&nbsp;创建人:%s'%(account.name,account.name_abbr,account.create_user)} for account in accounts]
        })
        status = 200
    except:
        data['msg'] = u"账户列表更新失败"
        error = traceback.format_exc()
        print error
    return HttpResponse(json.dumps({
        'status':status,
        'result':data
    }, cls=LazyEncoder))
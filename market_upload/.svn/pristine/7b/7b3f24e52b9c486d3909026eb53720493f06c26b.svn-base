#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

import settings
from utils.decorator import render_to, login_required
from django.views.decorators.csrf import csrf_exempt
import logging

from django.contrib import auth
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib.auth import authenticate, login as jlogin, logout as jlogout
from releaseinfo import LOGIN_URL, ACCOUNT_AUTH_URL, PRODUCT_URL, SPECIAL_USERS
from service import _user, _product
import urllib, urllib2
import json

logger = logging.getLogger('logger')

MENUS = {
    u"业务接入": "config",
}

@render_to("login.html")
@csrf_exempt
def login(request):
    '''
    @note: 接收用户名和密码并完成登录跳转功能，登录成功进入首页，登录失败不跳转
    '''
    redirect_to = request.REQUEST.get("next", reverse('index'))
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            logger.debug("[user login] %s login ok."%(username))
            return HttpResponseRedirect(redirect_to)

        if user and not user.is_active:
            error_msg = u'账号未激活'
        else:
            error_msg = u'账号或密码错误，请重新输入'

    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(redirect_to)
    
    TEMPLATE = "login.html"
    return locals()

def logout(request):
    jlogout(request)
    return HttpResponseRedirect(LOGIN_URL)

@login_required
@render_to("index.html")
def index(request):
#    guid = request.GET.get('VerifyId')
#    if not guid:
#        return HttpResponseRedirect(LOGIN_URL)
#    data = {'action':'checkguid1','Guid':guid}
#    req = urllib2.Request(ACCOUNT_AUTH_URL)
#
#    params = urllib.urlencode(data)
#    response = urllib2.urlopen(req, params)
#    jsonText = response.read()
#    return_dict = json.loads(jsonText)
#    
#    if not return_dict:
#        return HttpResponseRedirect(LOGIN_URL)
#    
#    username = return_dict.get('sAccount')
#    name = return_dict.get('sUserName')
#    uid= return_dict.get('iUserID')
#        
#    #user
#    u = _user.get_or_create_user_by_params(username=username)[0]
#    u.set_password(username)
#    u.first_name=name
#    u.save()
#    
#    user = authenticate(username=u.username, password=u.username)
#    jlogin(request, user)
    
    user = request.user
    #products_list
    products_add = []
    user.has_perm_config = False
    try:
        name = user.first_name
        if user.username in SPECIAL_USERS:
            name = u'张延礼'
        data = {'username':name.encode('utf8'),}
        
        req = urllib2.Request(PRODUCT_URL)
        params = urllib.urlencode(data)
        response = urllib2.urlopen(req, params)
        
        jsonText = response.read()
        json_dict= json.loads(jsonText)
        user_type = json_dict.get('type')
        if user_type == 2:
            user.has_perm_config = True
        product_dict_list = json_dict.get('items')
        for product_dict in product_dict_list:
            products_name = product_dict.get('VERSION_NAME')
            products_add.append(products_name)
    except Exception,e:
        print e
    
    products = _product.get_products_by_params(name__in=products_add)
    return locals()
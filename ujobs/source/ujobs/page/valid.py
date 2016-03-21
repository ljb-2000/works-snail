#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Created on 2014-8-21

@author: wx
'''
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as jlogin
from utils.decorator import render_to, login_required
from releaseinfo import ACCOUNT_AUTH_URL, SNAIL_ACCOUNT_URL, SNAIL_SHIELD_URL, H_APPID, H_PWD
from settings import LOGIN_URL
from service import _user
import logging
import urllib, urllib2
import json

logger = logging.getLogger("logger")

code_dict = {
201006:    '帐号未提供',
202019:    '动态密码未提供',
201001:    '账户不存在',
201004:    '账户已经被锁定',
201005:    '账户状态异常',
202001:    '未绑定',
202008:    '令牌已经过期',
202004:    '验证出错',
202007:    '令牌需要校验',
202006:    '密码已经过期',
}

@render_to("valid.html")
@csrf_exempt
def valid(request):
    '''
    @author: wx
    @param request: 请求参数
    @note: 接收蜗牛通行证和动态密码并完成验证跳转功能，登录成功进入首页，登录失败不跳转
    @return: 登录数据
    '''
    
    if request.method == "GET":
        guid = request.GET.get('VerifyId')
        if not guid:
            return HttpResponseRedirect(LOGIN_URL)
        
        data = {'action':'checkguid1','Guid':guid}
        req = urllib2.Request(ACCOUNT_AUTH_URL)
    
        params = urllib.urlencode(data)
        response = urllib2.urlopen(req, params)
        jsonText = response.read()
        return_dict = json.loads(jsonText)
        if not return_dict:
            return HttpResponseRedirect(LOGIN_URL)
        
        #user
        username = return_dict.get('sAccount')
        name = return_dict.get('sUserName')
        uid= return_dict.get('iUserID')
        if None in [username, name, uid]:
            return HttpResponseRedirect(LOGIN_URL)
        
        u = _user.get_or_create_user_by_params(username=username)[0]
        u.set_password(username)
        u.first_name=name
        u.last_name=uid
        u.save()
        
        #login
        user = authenticate(username=u.username, password=u.username) 
        jlogin(request, user)
    
    elif request.method == "POST":
        user = request.user
        account_name = request.POST.get('account_name')
        valid_code = request.POST.get('valid_code')
        if account_name and valid_code:
            logger.debug("[account valid] %s valid ..."%(account_name))
            redirect_to = request.REQUEST.get("next", reverse('overview'))
            
            data = {'passport':account_name,'dynamicPassword':valid_code}
            req = urllib2.Request(SNAIL_SHIELD_URL)
            req.add_header('H_APPID', H_APPID)
            req.add_header('H_PWD', H_PWD)
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            params = urllib.urlencode(data)
            
            response = urllib2.urlopen(req, params)
            jsonText = response.read()
            json_dict = json.loads(jsonText)
            state = json_dict.get('STATE')
            if state == '0':
                #valid
                try:
                    data = {'account':account_name}
                    req = urllib2.Request(SNAIL_ACCOUNT_URL)
                    req.add_header('H_APPID', H_APPID)
                    req.add_header('H_PWD', H_PWD)
                    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
                    params = urllib.urlencode(data)
                    
                    response = urllib2.urlopen(req, params)
                    jsonText = response.read()
                    json_dict = json.loads(jsonText)
                    account_name = json_dict.get('name','')
                    if account_name != user.first_name:
                        return HttpResponseRedirect(LOGIN_URL)
                    return HttpResponseRedirect(redirect_to)
                except:
                    return HttpResponseRedirect(LOGIN_URL)
            else:
                code = json_dict.get('CODE')
                if code:
                    error_msg = code_dict.get(code,'')
                    
    return locals()

from django.conf.urls import patterns, url
urlpatterns = patterns('',
    url(r'^$', valid, name='valid'),
    url(r'^valid/$', valid, name='valid'),
)

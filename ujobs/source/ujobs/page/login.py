#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Created on 2014-8-21

@author: wx
'''
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from utils.decorator import render_to
from django.views.decorators.csrf import csrf_exempt
import logging

#from mobile.sniffer.detect import detect_mobile_browser
#from mobile.sniffer.utilities import get_user_agent

logger = logging.getLogger("logger")

@render_to("login.html")
@csrf_exempt
def login(request):
    '''
    @author: wx
    @param request: 请求参数
    @note: 接收用户名和密码并完成登录跳转功能，登录成功进入验证页，登录失败不跳转
    @return: 登录数据
    '''
    guid = '9fb5eebbbe0446af8ea4ce5fa1d27083'
#    redirect_to = '/valid/?VerifyId=%s'%guid
    redirect_to = '/index/'
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

    TEMPLATE = "login_%s.html" % get_client_type(request)
    return locals()

def get_client_type(request):
    """
    @note: 返回客户访问类型，"web" or "mobile"
    """
#    user_agent_str = get_user_agent(request)
#    if detect_mobile_browser(user_agent_str):
#        if ('Android' in user_agent_str and 'Mobile' not in user_agent_str) or 'iPad' in user_agent_str or 'GT-P7510 Build/HMJ37' in user_agent_str:
#            return "web" #平板
#        else:
#            return "mobile" #手机
#    else:
#        return "web" #电脑
    return 'web'


from django.conf.urls import patterns, url
urlpatterns = patterns('',
    url(r'^$', login, name='login'),
    url(r'^login/$', login, name='login'),
)

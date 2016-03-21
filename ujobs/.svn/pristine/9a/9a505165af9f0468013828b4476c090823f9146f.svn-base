# -- encoding=utf-8 --
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from utils.decorator import render_to, login_required
from django.contrib.auth import authenticate, login as jlogin, logout as jlogout
from django.http import HttpResponseRedirect
import urllib, urllib2
import json
from settings import LOGIN_URL
from releaseinfo import ACCOUNT_AUTH_URL, FILE_SERVER_HOST, sysid
from enums.enum_user import MENUS

@login_required
@render_to("index.html")
def overview(request):
    '''
    @author: wx
    @param request: 请求参数
    @return: 首页数据
    @note:
    '''
    user = request.user
    uid = user.last_name
    
    #permission
    data = {'action':'getfuncjson1','SysId':sysid,'UID':uid}
    req = urllib2.Request(ACCOUNT_AUTH_URL)
    
    params = urllib.urlencode(data)
    response = urllib2.urlopen(req, params)
    jsonText = response.read()
    json_dict = json.loads(jsonText)
    userinfo_list = json_dict.get('userinfo',[])
    for userinfo in userinfo_list:
        perm_name = userinfo.get('sFunctionName')
        if perm_name and MENUS.get(perm_name):
            setattr(user,'has_perm_%s'%MENUS.get(perm_name),True)
        
    fileserver_url = FILE_SERVER_HOST
    return locals()

def logout(request):
    jlogout(request)
    return HttpResponseRedirect(LOGIN_URL)

from django.conf.urls import patterns, url
urlpatterns = patterns('',
    url(r'^overview/$', overview, name='overview'),
    url(r'^logout/$', logout, name='logout'),
)
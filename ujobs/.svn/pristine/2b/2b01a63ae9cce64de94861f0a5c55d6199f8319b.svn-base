# -- encoding=utf-8 --
import os, sys

sys.path.insert(0, os.path.abspath(os.curdir))

from utils.decorator import render_to, login_required
from releaseinfo import FILE_SERVER_HOST
from enums.enum_user import MENUS

@login_required
@render_to('index.html')
def index(request):
    user = request.user
    
    #permission
    for name,codename in MENUS.items():
#        if user.has_perm(u'custom.%s'%codename):
            setattr(user,'has_perm_%s'%codename,True)
    
    fileserver_url = FILE_SERVER_HOST
    return locals()

from django.conf.urls import patterns, url
urlpatterns = patterns('',
    url(r'^index/$', index, name='index'),
)
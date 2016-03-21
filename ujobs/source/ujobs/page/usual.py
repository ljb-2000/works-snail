# -- encoding=utf-8 --
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from utils.decorator import render_to, login_required
from django.views.decorators.csrf import csrf_exempt

@login_required
@render_to('usual/restart.html')
@csrf_exempt
def restart(request):
    return locals()

@login_required
@render_to('usual/modify_pwd.html')
@csrf_exempt
def modify_pwd(request):
    return locals()

@login_required
@render_to('usual/view_status.html')
@csrf_exempt
def view_status(request):
    return locals()

from django.conf.urls import patterns, url
urlpatterns = patterns('',
    url(r'^restart/$', restart, name='restart'),
    url(r'^modify_pwd/$', modify_pwd, name='modify_pwd'),
    url(r'^view_status/$', view_status, name='view_status'),
)
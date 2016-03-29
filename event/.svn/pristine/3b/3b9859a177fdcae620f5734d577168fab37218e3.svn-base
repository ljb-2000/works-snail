# -- encoding=utf-8 --
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from utils.decorator import render_to, login_required
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import datetime, time
import logging
import traceback
from utils.ctranslate import LazyEncoder
from django.db.transaction import commit_on_success

logger = logging.getLogger("logger")

@login_required
@csrf_exempt
@render_to('index.html')
def index(request):
#     user = request.user
    #permission
#     user = get_user_perm(user)
#     cnname = request.user.first_name
#     if request.user.username in SPECIAL_USERS:
#         cnname = SPECIAL_USER_NAME
#     p_list = get_product_list_by_user(cnname)
    return locals()



from django.conf.urls import patterns, url
urlpatterns = patterns('',
    url(r'^$', index, name='index'),
)
# -- encoding=utf-8 --
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from utils.decorator import render_to, login_required
from django.views.decorators.csrf import csrf_exempt
import datetime
from service import _account
from apps.accounts.forms import AccountForm
from settings import MAX_UPLOAD_SIZE
from releaseinfo import FILE_SERVER_HOST

@login_required
@render_to('send_file/contentDiv.html')
@csrf_exempt
def send_file(request):
    now = datetime.datetime.now()
    name = u'分发文件-%s'%datetime.datetime.strftime(now,'%Y%m%d%H%M%S')
    accounts = _account.get_accounts_by_params(is_delete=False)
    accountForm = AccountForm()
    max_upload_size = MAX_UPLOAD_SIZE
    user = request.user
    fileserver_url = FILE_SERVER_HOST
    return locals()

from django.conf.urls import patterns, url
urlpatterns = patterns('',
    url(r'^send_file/$', send_file, name='send_file'),
)
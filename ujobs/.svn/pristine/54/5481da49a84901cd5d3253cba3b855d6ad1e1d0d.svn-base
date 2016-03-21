#!/usr/bin/env python
# -*- coding:utf-8 -*-

# --------------------------------
# Author: shenjh@snail.com
# Date: 6/5/15
# Usage:
# --------------------------------

from django.conf.urls import patterns, url
from views import *

urlpatterns = patterns('ujobs.apps.files.views',
       url(r'^transfer/(?P<check_id>\d+)/$', send_file),
       url(r'^send_check/$', send_check),
       url(r'^upload/$', upload_file),
       url(r'^remote_file_exists/$', file_exists),
       url(r'^file_exists/$', file_info_exists),
       url(r'^ajax_show_page_detail/(?P<history_step_id>\d+)/$', ajax_show_page_detail),
       url(r'^ajax_show_ip_detail/(?P<history_step_id>\d+)/(?P<ip>.+)/$', ajax_show_ip_detail),
       url(r'^ajax_show_exec_type_detail/(?P<history_step_id>\d+)/(?P<exec_type>.+)/$', ajax_show_exec_type_detail),
)
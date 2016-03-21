#!/usr/bin/env python
# -*- coding:utf-8 -*-

# --------------------------------
# Author: shenjh@snail.com
# Date: 2015/10/14
# Usage:
# --------------------------------

from django.conf.urls import patterns, url
from views import get_agent_info


urlpatterns = patterns('ujobs.apps.usual.views',
   url(r'^agent_info/(?P<agent_ip>\d+.\d+.\d+.\d+)/$', get_agent_info),

)
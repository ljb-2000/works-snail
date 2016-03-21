# -- encoding=utf-8 --

'''
Created on 2015-5-22

@author: wx
'''

from django.conf.urls import patterns, url
from views import account_edit, account_del, ajax_add_account, get_account_list, get_account_list_v2

urlpatterns = patterns('ujobs.apps.usual.views',
   url(r'^edit/(\d+)/$', account_edit, name='account_edit'),
   url(r'^del/(\d+)/$', account_del, name='account_del'),
   url(r'^ajax_add_account/$', ajax_add_account, name='ajax_add_account'),
   url(r'^get_account_list/$', get_account_list),
   url(r'^get_account_list_v2/$', get_account_list_v2),
)
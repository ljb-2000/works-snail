# -- encoding=utf-8 --

'''
Created on 2015-5-22

@author: wx
'''

from django.conf.urls import patterns, url
from views import save, file_upload, download_file, ajax_get_product_option, ajax_get_productinfo, ajax_get_upload_info

urlpatterns = patterns('',
   url(r'^save/$', save, name='save'),
   url(r'^file_upload/$', file_upload, name='file_upload'),
   url(r'^download_file/$', download_file, name='download_file'),
   url(r'^ajax_get_product_option/$', ajax_get_product_option, name='ajax_get_product_option'),
   url(r'^ajax_get_productinfo/$', ajax_get_productinfo, name='ajax_get_productinfo'),
   url(r'^ajax_get_upload_info/$', ajax_get_upload_info, name='ajax_get_upload_info'),
)
# -- encoding=utf-8 --

from django.conf.urls import patterns, url
from views import job_list, job_add, job_view, job_delete, job_copy, job_step_edit, job_step_save, full_settings_save, job_start_now, template_job_sync, \
job_add_v2, job_view_v2, job_delete_v2, job_copy_v2, job_start_now_v2

urlpatterns = patterns('ujobs.apps.script.views',
   url(r'^job_list/(?P<template_id>\d+)/$', job_list),
   url(r'^job_add/$', job_add),
   url(r'^job_view/$', job_view),
   url(r'^job_delete/$', job_delete),
   url(r'^job_copy/$', job_copy),
   url(r'^job_start_now/(?P<job_id>\d+)/$', job_start_now),

#   url(r'^job_step/list/(?P<job_id>\d+)/$', job_step_list),
   url(r'^job_step/edit/(?P<job_step_id>\d+)/$', job_step_edit),
   url(r'^job_step/save/(?P<job_step_id>\d+)/$', job_step_save),
   url(r'^save_full_setting/(?P<job_id>\d+)/$', full_settings_save),
   
   url(r'^template_job_sync/$', template_job_sync),
   
   url(r'^job_add_v2/$', job_add_v2),
   url(r'^job_view_v2/$', job_view_v2),
   url(r'^job_delete_v2/$', job_delete_v2),
   url(r'^job_copy_v2/$', job_copy_v2),
   url(r'^job_start_now_v2/(?P<template_id>\d+)/$', job_start_now_v2),
)

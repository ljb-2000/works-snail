# -- encoding=utf-8 --

from django.conf.urls import patterns, url
from views import template_add, template_delete, \
    template_edit, template_step_list, template_step_add, \
    template_view, template_step_delete, template_step_edit, \
    template_step_save, full_settings_save, get_script_versions, \
    get_version_content, get_script_list,template_sort, \
    template_step_list_v2, template_step_edit_v2,template_clear_settings

urlpatterns = patterns('ujobs.apps.template.views',
       url(r'^add/$', template_add),
       url(r'^delete/(?P<template_id>\d+)/$', template_delete),
       url(r'^edit/(?P<template_id>\d+)/$', template_edit),
       url(r'^show/(?P<template_id>\d+)/$', template_view),
       url(r'^sort/(?P<template_id>\d+)/$', template_sort),
       url(r'^save_full_setting/(?P<template_id>\d+)/$', full_settings_save),
       url(r'^template_step/list/(?P<template_id>\d+)/$', template_step_list),
       url(r'^template_step/add/$', template_step_add),
       url(r'^template_step/delete/(?P<template_step_id>\d+)/$', template_step_delete),
       url(r'^template_step/edit/(?P<template_step_id>\d+)/$', template_step_edit),
       url(r'^template_step/save/(?P<template_step_id>\d+)/$', template_step_save),
       url(r'^get_script_versions/(?P<script_id>\d+)/$', get_script_versions),
       url(r'^get_version_content/(?P<version_id>\d+)/$', get_version_content),
       url(r'^get_script_list/$', get_script_list),
       
       url(r'^template_step/list_v2/(?P<template_id>\d+)/$', template_step_list_v2),
       url(r'^template_step/edit_v2/(?P<template_step_id>\d+)/$', template_step_edit_v2),
       url(r'^clear_settings/(?P<template_id>\d+)/$', template_clear_settings),
)

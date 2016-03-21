# -- encoding=utf-8 --

'''
Created on 2015-5-22

@author: wx
'''

from django.conf.urls import patterns, url
from views import question_list, add, edit, view, ajax_get_type_num, ajax_get_level_num, ajax_get_product_num, \
                ajax_get_question_title, ajax_get_question_describe, ajax_get_summarize

urlpatterns = patterns('ujobs.apps.usual.views',
    url(r'^list/$', question_list, name='question_list'),
    url(r'^add/$', add, name='add'),
    url(r'^edit/$', edit, name='edit'),
    url(r'^view/$', view, name='view'),
    url(r'^ajax_get_type_num/$', ajax_get_type_num, name='ajax_get_type_num'),
    url(r'^ajax_get_level_num/$', ajax_get_level_num, name='ajax_get_level_num'),
    url(r'^ajax_get_product_num/$', ajax_get_product_num, name='ajax_get_product_num'),
    url(r'^ajax_get_question_title/$', ajax_get_question_title, name='ajax_get_question_title'),
    url(r'^ajax_get_question_describe/$', ajax_get_question_describe, name='ajax_get_question_describe'),
    url(r'^ajax_get_summarize/$', ajax_get_summarize, name='ajax_get_summarize'),
)
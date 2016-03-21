#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--------------------------------
# Author: shenjh@snail.com
# Date: 2015-05-19
# Usage:
#--------------------------------

from django.conf.urls import patterns, url
from views import reboot, modify_pwd, show_status, ajax_get_reboot_returns, ajax_get_psw_returns, \
    ajax_get_cmdb_node_returns, ajax_get_cmdb_subnode_returns, ajax_get_cmdb_product_returns, \
    ajax_get_cmdb_ipvalid_returns, ajax_get_auth_emp_list_returns,update_auth, \
    ajax_get_cmdb_set_or_module, ajax_get_cmdb_ip_by_expression, \
    ajax_get_cmdb_ipvalid_returns_v2, ajax_get_cmdb_ip_by_expression_v2

urlpatterns = patterns('ujobs.apps.usual.views',
       url(r'^reboot/$', reboot),
       url(r'^modify_pwd/$', modify_pwd),
       url(r'^show_status/$', show_status),
       url(r'^update_auth/$', update_auth),
       url(r'^ajax_get_reboot_returns/$', ajax_get_reboot_returns),
       url(r'^ajax_get_psw_returns/$', ajax_get_psw_returns),
       url(r'^ajax_get_cmdb_node_returns/$', ajax_get_cmdb_node_returns),
       url(r'^ajax_get_cmdb_subnode_returns/$', ajax_get_cmdb_subnode_returns),
       url(r'^ajax_get_cmdb_product_returns/$', ajax_get_cmdb_product_returns),
       url(r'^ajax_get_cmdb_ipvalid_returns/$', ajax_get_cmdb_ipvalid_returns),
       url(r'^ajax_get_auth_emp_list_returns/$', ajax_get_auth_emp_list_returns),
       url(r'^ajax_get_cmdb_set_or_module/$', ajax_get_cmdb_set_or_module),
       url(r'^ajax_get_cmdb_ip_by_expression/$', ajax_get_cmdb_ip_by_expression),
       
       url(r'^ajax_get_cmdb_ipvalid_returns_v2/$', ajax_get_cmdb_ipvalid_returns_v2),
       url(r'^ajax_get_cmdb_ip_by_expression_v2/$', ajax_get_cmdb_ip_by_expression_v2),
)
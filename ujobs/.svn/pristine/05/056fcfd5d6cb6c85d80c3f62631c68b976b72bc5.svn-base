# -- encoding=utf-8 --
from django.conf.urls import patterns, include, url
from settings import STATIC_ROOT,MEDIA_ROOT
from enums import enum_page
from django.utils.importlib import import_module
from utils.pwd_valid import ajax_agent_valid, ajax_pwd_valid, ajax_pwd_valid_v2, ajax_cmdb_valid, ajax_cmdb_valid_v2

urlpatterns = patterns('',
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': STATIC_ROOT}),
    url(r'^file/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    url(r'^usual/', include('apps.usual.urls')),
    url(r'^script/', include('apps.script.urls')),
    url(r'^account/', include('apps.accounts.urls')),
    url(r'^files/', include('apps.files.urls')),
    url(r'^md_manage/', include('apps.template.urls')),
    url(r'^job/', include('apps.jobs.urls')),
    url(r'^history/', include('apps.history.urls')),
    url(r'^ajax_agent_valid/$', ajax_agent_valid),
    url(r'^ajax_pwd_valid/(\d+)/$', ajax_pwd_valid),
    url(r'^ajax_pwd_valid_v2/(\d+)/$', ajax_pwd_valid_v2),
    url(r'^ajax_cmdb_valid/$', ajax_cmdb_valid),
    url(r'^ajax_cmdb_valid_v2/$', ajax_cmdb_valid_v2),
    url(r'^api/', include('apis.urls')),
)

for view in enum_page.PAGES:
    v = import_module("page." + view)
    urlpatterns.extend(v.urlpatterns)
from django.conf.urls import patterns, include, url
#from django.contrib import admin
from settings import STATIC_ROOT,MEDIA_ROOT
from views import login, logout, index

urlpatterns = patterns('',
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': STATIC_ROOT}),
    url(r'^file/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    
    url(r'^$', login),
#    url(r'^$', index),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^index/$', index, name='index'),
    
    url(r'^product/', include('apps.product.urls')),
    
)

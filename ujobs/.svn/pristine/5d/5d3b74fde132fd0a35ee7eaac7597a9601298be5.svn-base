# -- encoding=utf-8 --

from django.conf.urls import patterns, url
from views import history_step_restart, history_step_stop, history_step_execute, history_step_skip
urlpatterns = patterns('ujobs.apps.history.views',
    url(r'^history_step_restart/$', history_step_restart),
    url(r'^history_step_stop/$', history_step_stop),
    url(r'^history_step_execute/$', history_step_execute),
    url(r'^history_step_skip/$', history_step_skip),
)

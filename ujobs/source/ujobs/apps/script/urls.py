# -- encoding=utf-8 --

from django.conf.urls import patterns, url
from views import ajax_script_upload, script_execute, script_detail,\
                  script_add, script_delete, script_edit, script_describe_edit, script_view,\
                  version_copy, version_delete, show_version_detail, version_remarks_edit, version_remarks_save,\
                  template_list, version_template_sync, version_job_sync,\
                  template_list_v2, version_template_sync_v2
urlpatterns = patterns('ujobs.apps.script.views',
   url(r'^script_execute/$', script_execute),
   url(r'^ajax_script_upload/$', ajax_script_upload),
   url(r'^script_detail/(\d+)/(\d+)/$', script_detail),
   
   url(r'^script_add/$', script_add),
   url(r'^script_delete/$', script_delete),
   url(r'^script_edit/$', script_edit),
   url(r'^script_describe_edit/$', script_describe_edit),
   url(r'^script_view/$', script_view),

   url(r'^version_copy/$', version_copy),
   url(r'^version_delete/$', version_delete),
   url(r'^show_version_detail/$', show_version_detail),
   url(r'^version_remarks_edit/$', version_remarks_edit),
   url(r'^version_remarks_save/$', version_remarks_save),
   url(r'^version_template_sync/$', version_template_sync),
   url(r'^version_job_sync/$', version_job_sync),
   url(r'^template_list/(?P<version_id>\d+)/$', template_list),
   
   url(r'^template_list_v2/(?P<version_id>\d+)/$', template_list_v2),
   url(r'^version_template_sync_v2/$', version_template_sync_v2),
)





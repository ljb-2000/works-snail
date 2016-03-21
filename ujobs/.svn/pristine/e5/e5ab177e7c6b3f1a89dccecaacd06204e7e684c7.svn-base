from django.contrib import admin

# Register your models here.
from models import *

class SaltJobAdmin(admin.ModelAdmin):
    list_display = ['jid','load','ctime']

admin.site.register(SaltJob,SaltJobAdmin)
admin.site.register(SaltReturn)
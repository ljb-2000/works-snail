#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

import django
django.setup()

from django.db.transaction import commit_on_success
from django.contrib.auth.models import User, Group
#from service.enums import ADMIN_GROUP

@commit_on_success
def add_users():
#    admin_group = Group.objects.get(name=ADMIN_GROUP)

    users = [("zhangyanl", "zhangyanl", u"张延礼"),
             ("wyi", "wyi", u"王毅"),
             ("wx", "wx", u"王鑫"),
             ("shenjh", "shenjh", u"沈建华"),
             ("luozh", "luozh", u"罗之浩")]
    
    for (uname, upw, first_name) in users:
        u = User.objects.get_or_create(username=uname)[0]
        u.set_password(upw)
        u.first_name = first_name
#        u.groups = [admin_group]
        print 'add user:', u
        u.save()
        
    print 'finish'
        
if __name__ == '__main__':
    add_users()

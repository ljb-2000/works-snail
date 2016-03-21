#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2015-6-30

@author: wx
'''
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

    users = [("zhangyanl", "zhangyanl"),
             ("wyi", "wyi"),
             ("wx", "wx"),
             ("shenjh", "shenjh"),
             ("luozh", "luozh")]
    
    for uname, upw in users:
        u = User.objects.get_or_create(username=uname)[0]
        u.set_password(upw)
#        u.groups = [admin_group]
        print 'add user:', u
        u.save()
        
    print 'finish'
        
if __name__ == '__main__':
    add_users()

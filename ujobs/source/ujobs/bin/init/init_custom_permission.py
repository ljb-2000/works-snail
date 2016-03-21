#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Created on 2015-9-24

@author: wangxin
'''
from service import _user
from enums.enum_user import MENUS

import django
django.setup()


def _init_page_permission(contenttype):
    for name,codename in MENUS.items():
        print 'add permission %s'%codename
        if name and codename:
            perm = _user.get_or_create_permission_by_params(name=name, content_type=contenttype, codename=codename)[0]
            
            user = _user.get_user_by_params(username='wx')
            user.user_permissions.add(perm)

def init_perms():
    contenttype = _user.get_custom_contenttype()
    _init_page_permission(contenttype)

if __name__ == '__main__':
    init_perms()

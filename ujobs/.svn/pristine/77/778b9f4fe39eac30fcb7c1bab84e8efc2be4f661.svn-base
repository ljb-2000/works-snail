#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Created on 2015-5-22

@author: wx
'''

from django import forms
#from django.core.exceptions import ValidationError
from models import Account

class AccountForm(forms.ModelForm):
    name = forms.CharField(error_messages={'required': u'请输入账户名称', 'unique': u'执行帐号名称已存在，请重新输入'})
    name_abbr = forms.CharField(error_messages={'required': u'请输入账户别名'})
    password = forms.CharField(widget=forms.PasswordInput, error_messages={'required': u'请输入账户密码'})
    
    class Meta:
        model = Account
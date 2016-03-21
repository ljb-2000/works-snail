#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------
# Author: shenjh@snail.com
# Date: 2015/8/4
# Usage:
# --------------------------------

from django import forms
from models import Template
from enums import enum_template

class AddTemplateForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': u"请填写作业名称，例如，版本发布，更新等",'style':"width:670px;"}),error_messages={'required': u'请输入作业名称'})
    template_type = forms.ChoiceField(choices=enum_template.USER_TEMPLATE_TYPES,error_messages={'required': u'请输入作业类型'})
    remarks = forms.CharField(widget=forms.Textarea(attrs={'placeholder': u"请输入作业备注",'rows':'4','class':'txtstyle','style':"width:670px;"}),error_messages={'required': u'请输入备注描述'})

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user',None)
        super(AddTemplateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Template
        fields = ['name','template_type','remarks']

    def clean_name(self):
        name = self.cleaned_data.get("name")
        try:
            Template.objects.get(name=name,create_user=self._user,is_delete=False)
            raise forms.ValidationError(u"您已经创建了该名称的模板")
        except Template.MultipleObjectsReturned:
            raise forms.ValidationError(u"当前用户存在多个同名模板")
        except Template.DoesNotExist:
            pass
        return name

class EditTemplateForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': u"请填写作业名称，例如，版本发布，更新等",'style':"width:670px;"}),error_messages={'required': u'请输入作业名称', 'unique': u'作业名称已存在，请重新输入'})
    template_type = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:684px;'}),choices=enum_template.USER_TEMPLATE_TYPES,error_messages={'required': u'请输入作业类型'})
    remarks = forms.CharField(widget=forms.Textarea(attrs={'placeholder': u"请输入作业备注",'rows':'4','class':'txtstyle','style':"width:670px;"}),error_messages={'required': u'请输入备注描述'})

    class Meta:
        model = Template
        fields = ['name','template_type','remarks']

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user',None)
        super(EditTemplateForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        try:
            if 'name' in self.changed_data:
                templates = Template.objects.filter(name=name,create_user=self._user,is_delete=False)
                if templates.count()>0:
                    raise forms.ValidationError(u"您已经创建了该名称的模板")
        except Template.DoesNotExist:
            pass
        return name
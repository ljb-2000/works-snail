# -*- coding: utf-8 -*-
'''
Created on 2015-5-26

@author: wx
'''

from django.utils.functional import Promise
from django.utils.translation import force_text
from simplejson import JSONEncoder

class LazyEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Promise):
            return force_text(o)
        else:
            return super(LazyEncoder, self).default(o)

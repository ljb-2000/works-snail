#!/usr/bin/env python
# -*- coding:utf-8 -*-

# --------------------------------
# Author: shenjh@snail.com
# Date: 6/23/15
# Usage:
# --------------------------------

from django import template
import json

register = template.Library()

@register.filter
def get_ips_length(ips_json):
    try:
        ips = json.loads(ips_json)
        return len(ips)
    except:
        return 0

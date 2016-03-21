#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import datetime
import requests
import traceback
from releaseinfo import PRODUCT_URL
from service import _report

def get_product_list_by_user(cnname):
    """
        get cn product list of user's cnname.
    """
    p_list = []
    if cnname:
        try:
            resp = requests.post(PRODUCT_URL,data={
                "username":cnname
            }).json()
            p_list=[item['productname'] for item in resp]
        except Exception,e:
            error = traceback.format_exc()
            print error
    return p_list

def get_department_list_by_user(user):
    """
        get department list of user
    """
    d_list = _report.get_departments_by_params(id=1)
    return d_list
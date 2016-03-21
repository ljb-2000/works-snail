#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

import django
django.setup()

from django.db.transaction import commit_on_success
from utils.util import get_product_list_by_user
from service import _report
from apps.report.models import STATUS1, STATUS2, STATUS3, STATUS4, STATUS5
from releaseinfo import SPECIAL_USER_NAME

@commit_on_success
def add_products():
    cnname = SPECIAL_USER_NAME
    product_names = get_product_list_by_user(cnname)
    for product_name in product_names:
        print 'add product:', product_name
        product = _report.get_or_create_product_by_params(name=product_name)[0]
        print 'add task_period:', product_name
        _report.get_or_create_taskPeriod_by_params(product=product,period=STATUS1)
        _report.get_or_create_taskPeriod_by_params(product=product,period=STATUS2)
        _report.get_or_create_taskPeriod_by_params(product=product,period=STATUS3)
        _report.get_or_create_taskPeriod_by_params(product=product,period=STATUS4)
        _report.get_or_create_taskPeriod_by_params(product=product,period=STATUS5)
        
    print 'finish'
        
if __name__ == '__main__':
    add_products()
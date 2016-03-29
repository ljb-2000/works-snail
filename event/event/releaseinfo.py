#encoding:utf-8

import os
REL_SITE_ROOT = os.path.dirname(os.path.abspath(__file__))

REL_STATIC_ROOT = os.path.join(REL_SITE_ROOT, 'static')

REL_DEBUG = True

DATABASE_ENGINE = 'django.db.backends.mysql'
DATABASE_NAME = 'event'
#DATABASE_USER = 'root'
#DATABASE_PASSWORD = 'snail'
#DATABASE_HOST = '10.206.2.24'
DATABASE_USER = 'root'
DATABASE_PASSWORD = 'root'
DATABASE_HOST = '172.18.80.170'
DATABASE_PORT = '3306'

REL_ROOT_PATH = 'http://127.0.0.1:7000'
REL_MEDIA_URL = '%s/file/' % REL_ROOT_PATH
REL_MEDIA_ROOT = os.path.join(REL_SITE_ROOT, 'file')



## ENTRY OF PLATFORM_HOST
PLATFORM_HOST = "http://10.103.4.19"

#LOGIN_URL = PLATFORM_HOST + '/index.htm'
LOGIN_URL = '/login/'

SPECIAL_USERS = ['wx', 'luozh', 'shenjh', 'wyi',]

# account auth of cmdb, get user permission.
ACCOUNT_AUTH_URL = PLATFORM_HOST + '/service/AccountHandler.ashx'

PRODUCT_URL = 'http://10.206.2.5/ops/cmdb/business/service/QueryProductByMt/'
PRODUCT_ALL_URL = 'http://10.206.2.5/ops/cmdb/server/service/QueryProduct/'
#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

import settings
from utils.decorator import render_to, login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.transaction import commit_on_success
from django.shortcuts import HttpResponse
import json
import datetime
import logging
import traceback

logger = logging.getLogger('logger')

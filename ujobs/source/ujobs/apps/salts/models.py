#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--------------------------------
# Author: shenjh@snail.com
# Date: 2015-05-20
# Usage:
#--------------------------------

from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class SaltJob(models.Model):
    '''
        store salt job commands.
    '''
    jid = models.CharField(max_length=255, verbose_name=_('Job id'))
    ctime = models.DateTimeField(verbose_name=_('Send Time'), auto_now_add=True)
    load = models.TextField(verbose_name=_('Command content'))

    class Meta:
        db_table = 'jids'
        verbose_name = _('Salt Job')
        verbose_name_plural = _('Salt Job')


class SaltReturn(models.Model):
    '''
        store salt job results.
    '''
    fun = models.CharField(max_length=255, verbose_name=_('Job Command'), blank=True, null=True)
    jid = models.CharField(max_length=255, verbose_name=_('Job Id'))
    minion_id = models.CharField(max_length=255, verbose_name=_('Minion Id'))
    success = models.CharField(max_length=10, verbose_name=_('Is Success'), blank=True, null=True, )
    ctime = models.DateTimeField(verbose_name=_('Receive Time'), auto_now_add=True)
    result = models.TextField(verbose_name=_('Return Content'))
    full_result = models.TextField(verbose_name=_('Full Return'))

    class Meta:
        db_table = 'salt_returns'
        verbose_name = _('Salt Return')
        verbose_name_plural = _('Salt Return')


#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--------------------------------
# Author: shenjh@snail.com
# Date: 2015-05-19
# Usage:
#--------------------------------

import releaseinfo as conf
import salt.client
import salt.runner
import salt.config

class SaltClient(salt.client.LocalClient):

    """
    Singleton pattern
    http://stackoverflow.com/questions/42558/python-and-the-singleton-pattern
    """

    _instance = None

    def __init__(self, config_path='/etc/salt/master'):
        salt.client.LocalClient.__init__(self, config_path)

    def __new__(cls, *args):
        if not cls._instance:
            cls._instance = super(SaltClient, cls).__new__(cls)
        return cls._instance


class RunnerClient(salt.runner.RunnerClient):

    _instance = None

    def __init__(self, config_path='/etc/salt/master'):
        opts = salt.config.master_config(config_path)
        salt.runner.RunnerClient.__init__(self, opts)

    def __new__(cls, *args):
        if not cls._instance:
            cls._instance = super(RunnerClient, cls).__new__(cls)
        return cls._instance

client = SaltClient(conf.SALT_MASTER_CONFIG)
runner = RunnerClient(conf.SALT_MASTER_CONFIG)

if __name__ == '__main__':
    print client.cmd('*','test.ping')
    print runner.cmd('manage.status', [])
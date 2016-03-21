#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--------------------------------
# Author: shenjh@snail.com
# Date: 2015-05-22
# Usage:
#--------------------------------

from ujobs.releaseinfo import REDIS_SERVER
import redis

class RedisClient(redis.StrictRedis):

    _instance = None

    def __init__(self, server):
        redis.StrictRedis.__init__(self, **server)

    def __new__(cls, *args):
        if not cls._instance:
            cls._instance = super(RedisClient, cls).__new__(cls)
        return cls._instance

    def refresh_set(self,key,values):
        rc.delete(key)
        if not values:
            return
        rc.sadd(key,*values)

rc = RedisClient(REDIS_SERVER)

if __name__ == '__main__':
    rc.set('test_key','this is a test.')
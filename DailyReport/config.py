# -*- coding: utf-8 -*-
import os
class Config(object):
    DEBUG = True
    CSRF_ENABLED = True
    COOKIE_EXPIRES = 60*60*48    #  24 hour
    #SECRET_KEY = os.urandom(24)
    SECRET_KEY = 'your secret key'
    ADMIN = 'xxxx'
    PASSWORD = 'xxxx'
    
    DB_USER = 'root'
    DB_PASSWORD = '123456'
    DB_HOST = '127.0.0.1'
    DB_NAME = 'dailyReport'
    SQLALCHEMY_DATABASE_URI = 'mysql://{0}:{1}@{2}/{3}?charset=utf8'.format(DB_USER,DB_PASSWORD,DB_HOST,DB_NAME)   

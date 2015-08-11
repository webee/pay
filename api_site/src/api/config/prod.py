# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import os


class App:
    TESTING = False
    DEBUG = False

class DataBase:
    HOST = os.environ['PAY_API_SITE_DATABASE_HOST']
    INSTANCE = 'lvye_pay'
    USERNAME = 'lvye_pay'
    PASSWORD = os.environ['PAY_API_SITE_DATABASE_PASSWORD']


class Celery:
    HOST = '127.0.0.1:5672'
    PASSWORD = 'p@55word'


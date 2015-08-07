# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import os


class DataBase:
    HOST = os.environ['DATABASE_HOST']
    INSTANCE = 'lvye_pay'
    USERNAME = 'lvye_pay'
    PASSWORD = os.environ['DATABASE_PASSWORD']

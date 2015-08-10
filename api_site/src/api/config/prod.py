# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import os


class DataBase:
    HOST = os.environ['PAY_API_DATABASE_HOST']
    INSTANCE = 'lvye_pay'
    USERNAME = 'lvye_pay'
    PASSWORD = os.environ['PAY_API_DATABASE_PASSWORD']

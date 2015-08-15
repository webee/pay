# coding=utf-8
import os


class DataBase:
    HOST = os.environ['PAY_API_SITE_DATABASE_HOST']
    USERNAME = 'lvye_pay'
    PASSWORD = os.environ['PAY_API_SITE_DATABASE_PASSWORD']
    INSTANCE = 'lvye_pay'

# -*- coding: utf-8 -*-
from fabric.api import local
from tools.log import *
from api import config


def init_db():
    #recreate_db()
    create_schema()
    inject_base_data()


def recreate_db():
    info('recreating database ...')
    local('mysql -u root -p < migration/init_db.sql')


def create_schema():
    info('creating schema ...')
    exec_sql_script('migration/schema_zyt.ddl')
    exec_sql_script('migration/schema_zyt_account.ddl')
    exec_sql_script('migration/schema_zyt_core.ddl')
    exec_sql_script('migration/schema_zyt_secured_transaction.ddl')


def exec_sql_script(script_name):
    local('mysql -h {} -u {} -p{} {} < {}'.format(
        config.DataBase.HOST,
        config.DataBase.USERNAME,
        config.DataBase.PASSWORD,
        config.DataBase.INSTANCE,
        script_name))


def inject_base_data():
    info('injecting base data ...')
    exec_sql_script('migration/data_zyt_account.ddl')

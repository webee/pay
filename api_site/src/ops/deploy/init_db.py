# -*- coding: utf-8 -*-
from fabric.api import local
from pytoolbox.util.console_log import *
from ops.config import db as config
import pytoolbox.conf.config as conf


def init_db(env, recreate=False):
    env = env or 'dev'
    conf.load(config, env=env)

    if recreate:
        recreate_db()
    create_schema()
    inject_base_data()


def recreate_db():
    info('recreating database ...')
    local('mysql -u root -p < migration/init_db.sql')


def create_schema():
    info('creating schema ...')
    exec_sql_script('migration/schema_zyt_account.ddl')
    exec_sql_script('migration/schema_zyt_core.ddl')
    exec_sql_script('migration/schema_zyt_secured_transaction.ddl')
    exec_sql_script('migration/schema_zyt_direct_transaction.ddl')
    exec_sql_script('migration/schema_zyt_charged_withdraw.ddl')


def exec_sql_script(script_name):
    local('mysql -h {} -u {} -p{} {} < {}'.format(
        config.HOST,
        config.USERNAME,
        config.PASSWORD,
        config.INSTANCE,
        script_name))


def inject_base_data():
    info('injecting base data ...')
    exec_sql_script('migration/data_zyt_account.sql')

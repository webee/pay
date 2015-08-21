# -*- coding: utf-8 -*-
from fabric.api import local
from tools.log import *
from ops.config import db as config
from pytoolbox.util import pmc_config


def init_db(env, recreate=False):
    env = env or 'dev'
    pmc_config.register_config(config, env=env)

    if recreate:
        recreate_db()
    create_schema()
    inject_base_data()


def recreate_db():
    info('recreating database ...')
    local('mysql -u root -p < migration/init_db.sql')


def create_schema():
    info('creating schema ...')
    exec_sql_script('migration/schema_zyt_pub_site.ddl')


def exec_sql_script(script_name):
    local('mysql -h {} -u {} -p{} {} < {}'.format(
        config.HOST,
        config.USERNAME,
        config.PASSWORD,
        config.INSTANCE,
        script_name))


def inject_base_data():
    info('injecting base data ...')

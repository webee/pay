# -*- coding: utf-8 -*-
from fabric.api import local
from tools.log import *
from pytoolbox import config


db_instance = config.get('database', 'instance')


def init_db():
    recreate_db()
    create_schema_2()
    inject_base_data()


def recreate_db():
    info('recreating database ...')
    local('mysql -u root -p < migration/init_db.sql')


def create_schema_2():
    info('creating schema ...')
    local('mysql -u root {} -p < migration/schema_zyt.ddl'.format(db_instance))
    local('mysql -u root {} -p < migration/schema_zyt_account.ddl'.format(db_instance))
    local('mysql -u root {} -p < migration/schema_zyt_core.ddl'.format(db_instance))
    local('mysql -u root {} -p < migration/schema_zyt_secured_transaction.ddl'.format(db_instance))
    local('mysql -u root {} -p < migration/schema_zyt_pub_site.ddl'.format(db_instance))


def inject_base_data():
    info('injecting base data ...')
    local('mysql -u root {} -p < migration/data_zyt_account.sql'.format(db_instance))

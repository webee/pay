# -*- coding: utf-8 -*-
from fabric.api import local
from tools.log import *
from pytoolbox import config


db_instance = config.get('database', 'instance')


def init_db():
    recreate_db()
    create_schema()
    init_test_data()


def init_db_2():
    recreate_db()
    create_schema_2()
    inject_base_data()


def recreate_db():
    info('recreating database ...')
    local('mysql -u root -p < db/init_db.sql')


def create_schema():
    info('creating schema ...')
    local('mysql -u root {} -p < db/schema.ddl'.format(db_instance))
    local('mysql -u root {} -p < db/schema_zyt_pub_site.ddl'.format(db_instance))


def create_schema_2():
    info('creating schema ...')
    local('mysql -u root {} -p < db/schema_zyt.ddl'.format(db_instance))
    local('mysql -u root {} -p < db/schema_zyt_account.ddl'.format(db_instance))
    local('mysql -u root {} -p < db/schema_zyt_core.ddl'.format(db_instance))
    local('mysql -u root {} -p < db/schema_zyt_secured_transaction.ddl'.format(db_instance))
    local('mysql -u root {} -p < db/schema_zyt_pub_site.ddl'.format(db_instance))


def inject_base_data():
    info('injecting base data ...')
    local('mysql -u root {} -p < db/data_zyt_account.sql'.format(db_instance))


def init_test_data():
    info('initing test data ...')
    local('mysql -u root {} -p < db/init_test_data.sql'.format(db_instance))

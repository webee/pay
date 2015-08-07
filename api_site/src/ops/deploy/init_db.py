# -*- coding: utf-8 -*-
from fabric.api import local
from tools.log import *
from api import config


_db_instance = config.DataBase.INSTANCE


def init_db():
    recreate_db()
    create_schema_2()
    inject_base_data()


def recreate_db():
    info('recreating database ...')
    local('mysql -u root -p < migration/init_db.sql')


def create_schema_2():
    info('creating schema ...')
    local('mysql -u root {} -p < migration/schema_zyt.ddl'.format(_db_instance))
    local('mysql -u root {} -p < migration/schema_zyt_account.ddl'.format(_db_instance))
    local('mysql -u root {} -p < migration/schema_zyt_core.ddl'.format(_db_instance))
    local('mysql -u root {} -p < migration/schema_zyt_secured_transaction.ddl'.format(_db_instance))
    local('mysql -u root {} -p < migration/schema_zyt_pub_site.ddl'.format(_db_instance))


def inject_base_data():
    info('injecting base data ...')
    local('mysql -u root {} -p < migration/data_zyt_account.sql'.format(_db_instance))

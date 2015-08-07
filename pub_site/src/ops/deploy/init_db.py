# -*- coding: utf-8 -*-
from fabric.api import local
from tools.log import *
from pub_site import config


_db_instance = config.DataBase.INSTANCE


def init_db():
    recreate_db()
    create_schema()
    inject_base_data()


def recreate_db():
    info('recreating database ...')
    local('mysql -u root -p < migration/init_db.sql')


def create_schema():
    info('creating schema ...')
    local('mysql -u root {} -p < migration/schema_zyt_pub_site.ddl'.format(_db_instance))


def inject_base_data():
    info('injecting base data ...')

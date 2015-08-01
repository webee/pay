# -*- coding: utf-8 -*-
from fabric.api import local
from tools.log import *
from pytoolbox.conf import config


db_instance = config.get('hosts', 'instance')


def init_db():
    recreate_db()
    create_schema()
    init_test_data()


def recreate_db():
    info('recreating database ...')
    local('mysql -u root -p < db/init_db.sql')


def create_schema():
    info('creating schema ...')
    local('mysql -u root {} -p < db/schema.ddl'.format(db_instance))


def init_test_data():
    info('initing test data ...')
    local('mysql -u root {} -p < db/init_test_data.sql'.format(db_instance))

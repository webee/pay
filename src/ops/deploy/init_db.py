# -*- coding: utf-8 -*-
from fabric.api import local
from tools.log import *
import file_config

cfg = file_config.config()


def init_db():
    recreate_db()
    create_schema()
    init_test_data()


def recreate_db():
    info('recreating database ...')
    local('mysql -u root -p < db/init_db.sql')


def create_schema():
    info('creating schema ...')
    local('mysql -u root {} -p < db/schema.ddl'.format(cfg.get('database', 'instance')))


def init_test_data():
    info('initing test data ...')
    local('mysql -u root {} -p < db/init_test_data.sql'.format(cfg.get('database', 'instance')))

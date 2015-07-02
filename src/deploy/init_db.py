# -*- coding: utf-8 -*-
from fabric.api import local
from tool.log import *
import config

cfg = config.config()

def init_db():
    recreate_db()
    create_schema()


def recreate_db():
    info('recreating database ...')
    local('mysql -u root -p < db/init_db.sql')


def create_schema():
    info('creating schema ...')
    local('mysql -u root -p {} < db/schema.sql'.format(cfg.get('database','instance')))


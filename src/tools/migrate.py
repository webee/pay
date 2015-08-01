# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import os
import sys
from tools.dbe import from_db
from log import *
from fabric.api import local
from pytoolbox.conf import config


def migrate():
    versions = load_versions()
    if len(versions) == 0:
        warn('No migration script found!')
        sys.exit(0)
    latest_version = get_database_latest_version()
    version_numbers = sorted(versions.keys())
    if latest_version > version_numbers[-1]:
        error('Error: database version is late than migration script, SOMETHING WRONG!')
        sys.exit(-1)
    elif latest_version == version_numbers[-1]:
        info('database version [{}] is up to date'.format(latest_version))
        sys.exit(0)
    for version_number in version_numbers:
        if version_number > latest_version:
            info('migrating: {}'.format(versions[version_number]))
            execute_script(versions[version_number])
            update_database_version(version_number)

    warn('database migration finished, from {} to {}'.format(latest_version, version_numbers[-1]))


def execute_script(script_file_name):
    db_instance = config.get('database', 'instance')
    username = config.get('database', 'user')
    password = config.get('database', 'password')
    local('mysql -u {} -p{} {} < {}'.format(username, password, db_instance, script_file_name))


def update_database_version(version):
    from_db().execute('update db_migration set latest_version=%(version)s', version=version)


def get_database_latest_version():
    return from_db().get_scalar('SELECT latest_version FROM db_migration')


def load_versions():
    versions = {}
    for file_name in os.listdir('db'):
        if '-' in file_name and file_name.endswith('.sql'):
            version = int(file_name.split('-')[0])
            versions[version] = 'db/{}'.format(file_name)
    return versions

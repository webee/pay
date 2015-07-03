# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from fabric.api import local
from tools.log import *


def restart_pub():
    try:
        local("pgrep -lf uwsgi-pub.sock | awk {'print $1'} | xargs kill -9")
    except:
        warn('unable to stop the uwsgi process...')
    local('./pub_up')


def server_up():
    local('sudo /usr/local/nginx/sbin/nginx')
    local('sudo service mysqld start')

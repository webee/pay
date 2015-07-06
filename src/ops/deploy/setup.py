# -*- coding: utf-8 -*-
from fabric.api import local

def update_env():
    install_dependencies()

def install_dependencies():
    pip_install('-r requirements.txt')


def yum_install(package):
    local('sudo yum install -y {}'.format(package))

def pip_install(package):
    local('pip install {}'.format(package))

def npm_intall(package):
    local('npm install {}'.format(package))
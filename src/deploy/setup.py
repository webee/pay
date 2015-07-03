# -*- coding: utf-8 -*-
from fabric.api import local

def update_env():
    install_dependencies()

def install_dependencies():
    pip_install('flask')
    pip_install('requests')
    pip_install('mysql-python')
    pip_install('markupsafe')
    pip_install('uwsgi')



def yum_install(package):
    local('sudo yum install -y {}'.format(package))

def pip_install(package):
    local('pip install {}'.format(package))

def npm_intall(package):
    local('npm install {}'.format(package))
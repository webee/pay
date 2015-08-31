# -*- coding: utf-8 -*-
import fabric.api as fab

from pytoolbox.util import pmc_config
from ops.config import deploy as config


def init_config(env):
    import os

    env = env or 'dev'
    os.environ['ENV'] = env
    pmc_config.register_config(config, env=env)


def deploy(env, name, do_deploy=True):
    init_config(env)

    fab.use_ssh_config = True
    fab.env.host_string = config.HOST_STRING
    code_dir = config.CODE_DIR
    root_dir = "{}/../".format(code_dir)
    update_code(code_dir, root_dir)

    with fab.cd(code_dir), fab.prefix('source %s/bin/activate' % config.VENV_NAME):
        update_requirements()

        if do_deploy:
            update_deploy_file(name)
            stop_python_server(name)
            start_python_server(name)


def update_code(code_dir, root_dir):
    with fab.cd(code_dir):
        fab.run('git pull --ff-only origin master')

    with fab.cd(root_dir):
        fab.run('git submodule update')


def update_requirements():
    fab.run('pip install -r requirements.txt')


def update_deploy_file(file_name):
    fab.run('sudo cp deploy/{}.conf /etc/supervisord.d/'.format(file_name))
    fab.run('sudo /usr/local/bin/supervisorctl reread')
    fab.run('sudo /usr/local/bin/supervisorctl update')


def stop_python_server(name):
    fab.run('sudo /usr/local/bin/supervisorctl stop {}'.format(name))


def start_python_server(name):
    fab.run('sudo /usr/local/bin/supervisorctl start {}'.format(name))

# -*- coding: utf-8 -*-
import fabric.api as fab
from contextlib import contextmanager


def init_config(env):
    from pytoolbox.util import pmc_config
    from ops.config import deploy as config
    import os

    env = env or 'dev'
    os.environ['ENV'] = env
    pmc_config.register_config(config, env=env)

    return config


def deploy(env, name, manager_name="manager", do_deploy=True):
    config = init_config(env)

    with require_cmd_context(config):
        upgrade_db(manager_name, env)
        if do_deploy:
            update_deploy_file(name)
            stop_python_server(name)
            start_python_server(name)


def db_migrate(env, manager_name):
    config = init_config(env)

    with require_cmd_context(config):
        upgrade_db(manager_name, env)


def upgrade_db(manager_name, env):
    fab.run('python src/%s.py -e %s db upgrade' % (manager_name, env))


@contextmanager
def require_cmd_context(env, config):
    fab.use_ssh_config = True
    fab.env.host_string = config.HOST_STRING
    code_dir = config.CODE_DIR
    root_dir = "{}/../".format(code_dir)
    update_code(env, code_dir, root_dir)

    with fab.cd(code_dir), fab.prefix('source %s/bin/activate' % config.VENV_NAME):
        update_requirements()

        yield


def update_code(env, code_dir, root_dir):
    with fab.cd(code_dir):
        branch = 'master' if env == 'prod' else env
        fab.run('git pull --ff-only origin %s' % branch)

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

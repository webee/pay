# -*- coding: utf-8 -*-
from pytoolbox.util import deploy_commons as dc


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

    with dc.require_cmd_context(env, config):
        #dc.upgrade_db(manager_name, env)
        if do_deploy:
            dc.update_deploy_file(name)
            dc.stop_python_server(name)
            dc.start_python_server(name)


def db_migrate(env, manager_name):
    config = init_config(env)

    with dc.require_cmd_context(config):
        dc.upgrade_db(manager_name, env)

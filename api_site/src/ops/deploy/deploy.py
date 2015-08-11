import fabric.api as fab


def get_config(env):
    import os
    from api import config
    import pytoolbox.conf.config as conf

    env = env or 'dev'
    os.environ['ENV'] = env
    conf.load(config, env=env)
    return config


def deploy(env):
    env = env or 'dev'
    cfg = get_config(env)
    fab.use_ssh_config = True
    fab.env.host_string = cfg.Deploy.HOST_STRING
    code_dir = cfg.Deploy.CODE_DIR
    with fab.cd(code_dir), fab.prefix('source api_venv/bin/activate'):
        fab.run('git pull --ff-only origin master')
        stop_python_server('pay_api_site')
        start_python_server('pay_api_site')


def stop_python_server(name):
    fab.run('/usr/local/bin/supervisorctl stop {}'.format(name))


def start_python_server(name):
    fab.run('/usr/local/bin/supervisorctl start {}'.format(name))

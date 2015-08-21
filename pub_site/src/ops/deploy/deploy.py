import fabric.api as fab


def get_config(env):
    import os
    from ops.config import deploy as config
    from pytoolbox.util import pmc_config

    env = env or 'dev'
    os.environ['ENV'] = env
    pmc_config.register_config(config, env=env)
    return config


def deploy(env):
    env = env or 'dev'
    cfg = get_config(env)
    fab.use_ssh_config = True
    fab.env.host_string = cfg.HOST_STRING
    code_dir = cfg.CODE_DIR
    toolbox_dir = "{}/../libraries/pytoolbox".format(code_dir)
    with fab.cd(toolbox_dir):
        fab.run('git pull --ff-only origin master')
    with fab.cd(code_dir), fab.prefix('source pub_venv/bin/activate'):
        fab.run('git pull --ff-only origin master')
        renew_config_file()
        stop_python_server('pay_pub_site')
        start_python_server('pay_pub_site')


def stop_python_server(name):
    fab.run('sudo /usr/local/bin/supervisorctl stop {}'.format(name))


def start_python_server(name):
    fab.run('sudo /usr/local/bin/supervisorctl start {}'.format(name))

def renew_config_file():
    fab.run('sudo cp deploy/pay_pub_site.conf /etc/supervisord.d/')
    fab.run('sudo /usr/local/bin/supervisorctl reread')
    fab.run('sudo /usr/local/bin/supervisorctl update')

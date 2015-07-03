import config
import fabric.api as fab
from tools.log import warn

cfg = config.config()
fab.use_ssh_config = True
fab.env.host_string = cfg.get('deploy', 'prod.host')


def deploy(update_env=None):
    code_dir = cfg.get('dev.code.dir')
    with fab.cd(code_dir):
        fab.run('git pull --ff-only origin master')
        if update_env:
            fab.run('./dev update_env')
        fab.run('./dev migrate')
        restart_uwsgi_server('pub')
        restart_uwsgi_server('op')


def restart_uwsgi_server(name):
    try:
        fab.run("pgrep -lf uwsgi-{}.sock | awk {'print $1'} | xargs kill -9".format(name))
    except:
        warn('unable to stop the uwsgi-{} process...'.format(name))
    fab.run('./{}_up'.format(name))


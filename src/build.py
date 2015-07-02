from deploy import *
from dev import *
import logging


logging.basicConfig(format='[%(name)s-%(levelname)s]%(asctime)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.DEBUG)
logging.getLogger('fabric').setLevel(logging.WARNING)
logging.getLogger('paramiko').setLevel(logging.WARNING)


def init_user():
    from deploy.create_user import init_user

    init_user()


def migrate():
    from tool.migrate import migrate

    migrate()


def server_up():
    from dev.local import server_up

    server_up()

def mock_sendgrid_notify():
    from dev.local import mock_sendgrid_notify
    mock_sendgrid_notify()

if __name__ == '__main__':
    import sys

    command = sys.argv[1]
    args = sys.argv[2:]
    module = __import__('build')
    method = getattr(module, command)
    if args:
        method(*args)
    else:
        method()


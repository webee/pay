# coding=utf-8
from tools.pmc_config import register_config, get_project_root

PROJECT_ROOT = get_project_root()


def load_config(env):
    register_config(__name__, 'etc', env=env)
    register_config(__name__, 'lianlian_pay', env=env)
    register_config(__name__, 'test_pay', env=env)

    # business
    register_config(__name__, 'application', env=env)

    # celery
    register_config(__name__, 'api_celery_task', env=env)

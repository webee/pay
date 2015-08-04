# coding=utf-8
from tools.pmc_config import register_config, get_project_root

configs = {}
PROJECT_ROOT = get_project_root()

register_config(__name__, 'api')
register_config(__name__, 'db')
register_config(__name__, 'deploy')
register_config(__name__, 'lianlian', mapping={'testing': ['test']})
register_config(__name__, 'api_task_celery')

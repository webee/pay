# coding=utf-8
from .utils import register_config, get_project_root

configs = {}
PROJECT_ROOT = get_project_root()

register_config(__name__, 'api')
register_config(__name__, 'db')
register_config(__name__, 'deploy')

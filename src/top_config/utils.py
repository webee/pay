# coding=utf-8
import os
from types import ClassType, ModuleType
from tools.mylog import get_logger

logger = get_logger(__name__)

_profiles_mapping = {
    'development': 'dev',
    'testing': 'test',
    'production': 'prod'
}


def register_config(parent, name, mapping=None):
    """ 注册配置
    :param parent: 所在包
    :param name: 模块名
    :return:
    """
    import top_config
    config_package = __import__('{0}.{1}'.format(parent, name), fromlist=[parent])
    # import default
    setattr(config_package, '__config_name__', 'default')
    setattr(config_package, '__members__', {})
    _register_config(config_package, config_package)

    config_name = _get_config_name(name, mapping)
    if config_name != 'default':
        config_mod = _get_package_mod(config_package, config_name)
        if config_mod:
            _register_config(config_package, config_mod)
            setattr(config_package, '__config_name__', config_name)
        else:
            logger.warn("config not found: [{0}.{1}]".format(name, config_name))
        _safe_del_attr(config_package, config_name)
    # remove none-config vars.
    _remove_none_config_vars(config_package)
    # add to configs.
    top_config.configs[config_package.__name__] = {'name': name,
                                                   'config': config_package.__config_name__,
                                                   'members': config_package.__members__}
    logger.info("use config : [{0}.{1}]".format(name, config_package.__config_name__))


def _get_package_mod(pack, name, need_reload=False):
    """ from pack import name
    """
    try:
        return __import__('{0}.{1}'.format(pack.__name__, name), fromlist=[pack.__name__])
    except Exception as e:
        logger.warn('{0}, {1}'.format(e.message, pack.__name__))


def _is_valid_config_var_name(mod, n):
    """ there are two types of config vars, Class and None-Class.
    :param mod: where var n in.
    :param n: var name.
    :return:
    """
    v = getattr(mod, n)
    if isinstance(v, ClassType):
        return n[0].isupper()
    return n[0].isalpha() and n.isupper()


def _register_config(config_package, config_mod):
    """ merge config vars from config_mod to config_package.
    :param config_package:
    :param config_mod:
    :return:
    """
    for x in [i for i in dir(config_mod) if _is_valid_config_var_name(config_mod, i)]:
        v = getattr(config_mod, x)
        _merge_config_value(config_package, x, v, fromp=config_mod.__name__)


def _merge_config_value(config_package, x, v, fromp=None):
    if not hasattr(config_package, x):
        logger.warn('[{0}] has no attr [{1}]'.format(config_package.__name__, x))
    else:
        orig_v = getattr(config_package, x)
        if isinstance(orig_v, ClassType) and isinstance(v, ClassType):
            for _x in [i for i in dir(v) if _is_valid_config_var_name(v, i)]:
                _v = getattr(v, _x)
                _merge_config_value(orig_v, _x, _v, fromp='{0}.{1}'.format(fromp, v.__name__))

            if not hasattr(config_package, '__members__'):
                setattr(config_package, '__members__', {})
            config_package.__members__[x] = orig_v.__members__
            return
    setattr(config_package, x, v)
    if not hasattr(config_package, '__members__'):
        setattr(config_package, '__members__', {})
    config_package.__members__[x] = {'value': v, 'from': fromp}


def _remove_none_config_vars(config_package):
    for x in [_ for _ in dir(config_package) if _[0].isalpha()]:
        v = getattr(config_package, x)
        if not _is_valid_config_var_name(config_package, x) and not isinstance(v, ModuleType):
            # keep modules.
            delattr(config_package, x)
            continue
        if isinstance(v, ClassType):
            _remove_none_config_vars(v)


def _safe_del_attr(mod, name):
    if hasattr(mod, name):
        delattr(mod, name)


def _get_config_name(name='SYSTEM', mapping=None):
    config = os.getenv('{0}_CONFIG'.format(name.upper()), os.getenv('SYSTEM_CONFIG', 'default'))
    config = _profiles_mapping.get(config, config)
    if mapping is None:
        return config
    for key, vs in mapping.items():
        if config in vs:
            return key
    return config


def get_project_root():
    from os.path import dirname, abspath
    return os.getenv('PROJ_ROOT', abspath(dirname((dirname(dirname(__file__))))))


def read_string(filepath, root=get_project_root()):
    from os import path
    with open(path.join(root, filepath)) as fin:
        return fin.read().strip('\n')


def inject_here_from_file(mod_path, filepath):
    config_package = __import__(mod_path, fromlist=[mod_path[:mod_path.rindex('.')]])
    # TODO

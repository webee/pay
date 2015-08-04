# coding=utf-8
"""
Package, module, class based config utils.
"""
import sys
import os
import re
import inspect
from types import ModuleType, FunctionType
from tools.mylog import get_logger

logger = get_logger(__name__)

_envs_mapping = {
    'development': 'dev',
    'testing': 'test',
    'production': 'prod',
    'qa': 'beta',
}

ENV_VAR_NAME = 'ENV'
DEFAULT_ENV = 'default'

CAMEL_NAMING_PATTERN = re.compile(r'([A-Z][a-z]*)+')


def register_config(parent_or_config, name=None, env=DEFAULT_ENV, mapping=None):
    """ 注册配置
    :param parent_or_config: 所在包
    :param name: 模块名
    :return:
    """
    if isinstance(parent_or_config, ModuleType):
        if name is None:
            config_package = parent_or_config
        else:
            config_package = __import__('{0}.{1}'.format(parent_or_config.__name__, name),
                                        fromlist=[parent_or_config.__name__])
    elif isinstance(parent_or_config, str):
        if name is None:
            config_package = __import__(parent_or_config, fromlist=[parent_or_config])
        else:
            config_package = __import__('{0}.{1}'.format(parent_or_config, name), fromlist=[parent_or_config])

    # import default
    setattr(config_package, '__env_name__', DEFAULT_ENV)
    setattr(config_package, '__members__', {})
    _register_config(config_package, config_package)

    env_name = _get_env_name(name, mapping, env=env)
    if env_name != DEFAULT_ENV:
        config_mod = _get_package_mod(config_package, env_name)
        if config_mod:
            _register_config(config_package, config_mod)
            setattr(config_package, '__env_name__', env_name)
        else:
            logger.warn("config not found: [{0}.{1}]".format(name, env_name))
        _safe_del_attr(config_package, env_name)
    # remove none-config vars.
    _remove_none_config_vars(config_package)
    # add to configs parent.
    configs_parent = _get_parent_module(config_package)
    setattr(configs_parent, '__pmc_configs__', {})
    _configs = getattr(configs_parent, '__pmc_configs__')
    _configs[config_package.__name__] = {'name': name,
                                         'config': config_package.__env_name__,
                                         'members': config_package.__members__}

    logger.info("use config : [{0}.{1}]".format(config_package.__name__, config_package.__env_name__))


def _get_parent_module(mod):
    mname = mod.__name__
    i = mname.rfind('.')
    if i < 0:
        return mod
    return sys.modules[mname[:i]]


def _get_package_mod(pack, name):
    """ from pack import name
    """
    try:
        return __import__('{0}.{1}'.format(pack.__name__, name), fromlist=[pack.__name__])
    except Exception as e:
        logger.warn('{0}, {1}'.format(e.message, pack.__name__))


def _is_camel_name(name):
    return CAMEL_NAMING_PATTERN.match(name) is not None


def _list_names(m):
    if isinstance(m, dict):
        return m.keys()
    return dir(m)


def _get_value(m, n):
    if isinstance(m, dict):
        return m.get(n)
    return getattr(m, n) if hasattr(m, n) else None


def _is_valid_config_member(mod, n):
    """ there are three types of config vars, Class, Module and None-[Class&Module].
    :param mod: where var n in.
    :param n: var name.
    :return:
    """
    v = _get_value(mod, n)
    if _is_class(v) or isinstance(v, (ModuleType, dict)):
        return _is_camel_name(n)
    elif isinstance(v, FunctionType):
        return False
    return n[0].isalpha() and n.isupper()


def _is_class(v):
    return inspect.isclass(v)


def _register_config(config_package, config_mod):
    """ merge config vars from config_mod to config_package.
    :param config_package:
    :param config_mod:
    :return:
    """
    for x in [i for i in dir(config_mod) if _is_valid_config_member(config_mod, i)]:
        v = getattr(config_mod, x)
        _merge_config_value(config_package, x, v, fromp=config_mod.__name__)


def _merge_config_value(config_package, x, v, fromp=None):
    """
    recursive merge configs.
    :param config_package:
    :param x:
    :param v:
    :param fromp:
    :return:
    """
    if not hasattr(config_package, x):
        logger.warn('[{0}] has no attr [{1}]'.format(config_package.__name__, x))
        logger.warn('[invalid config name [{1}]'.format(x))
    else:
        orig_v = getattr(config_package, x)
        if _is_class(orig_v) and _is_class(v):
            for _x in [i for i in dir(v) if _is_valid_config_member(v, i)]:
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
        if not _is_valid_config_member(config_package, x):
            delattr(config_package, x)
            continue
        if _is_class(v) or isinstance(v, ModuleType):
            _remove_none_config_vars(v)


def _safe_del_attr(mod, name):
    if hasattr(mod, name):
        delattr(mod, name)


def _get_env_name(name=ENV_VAR_NAME, mapping=None, env=None):
    if env is None:
        env = os.getenv(ENV_VAR_NAME, DEFAULT_ENV)
        if name is not None:
            env = os.getenv('{0}_ENV'.format(name.upper()), env)
        env = _envs_mapping.get(env, env)

    if mapping is None:
        return env
    for key, vs in mapping.items():
        if env in vs:
            return key
    return env


def get_project_root():
    from os.path import dirname, abspath
    return os.getenv('PROJ_ROOT', abspath(dirname((dirname(dirname(__file__))))))


def read_string(filepath, root=get_project_root()):
    from os import path
    with open(path.join(root, filepath)) as fin:
        return fin.read().strip('\n')


def _merge_data(target_mod, x, v):
    orig_v = _get_value(target_mod, x)

    if (orig_v is None or _is_class(orig_v)) and isinstance(v, dict):
        if orig_v is None:
            orig_v = type(x, (object,), {'__name__': '{0}.{1}'.format(target_mod.__name__, x)})
            setattr(target_mod, x, orig_v)
            orig_v = _get_value(target_mod, x)

        for _x in [i for i in _list_names(v) if _is_valid_config_member(v, i)]:
            _v = _get_value(v, _x)
            _merge_data(orig_v, _x, _v)
        return
    if not isinstance(v, dict):
        setattr(target_mod, x, v)


def _inject_data(target_mod, data):
    for x in [i for i in data.keys() if _is_valid_config_member(data, i)]:
        v = _get_value(data, x)
        _merge_data(target_mod, x, v)


def _get_deep_value(data, names=()):
    for name in names:
        return _get_deep_value(data[name], names[1:])
    return data


def cover_inject_from_file(mod_path, yaml_file, path="", root=get_project_root()):
    """ insert configs from a yaml file section specified by path.
    :param mod_path:
    :param yaml_file:
    :param path: dot sperated names, eg. xx.yy.zzz
    :param root: file root dir.
    :return:
    """
    import yaml
    target_mod = __import__(mod_path, fromlist=[mod_path])

    data = yaml.load(open(os.path.join(root, yaml_file)))
    names = path.split('.') if path else ()
    data = _get_deep_value(data, names)

    _inject_data(target_mod, data)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import wraps
import urlparse
from flask import request
from api_x.utils import response
from pytoolbox.util.log import get_logger
from pytoolbox.util.sign import Signer
from api_x.zyt.user_mapping import get_channel_by_name
from api_x.config import etc as config


logger = get_logger(__name__)

_func_idx_api_entries = {}
_name_idx_api_entries = {}


def _register_api_entry(f, name, multi_entries=False):
    """
    注册api入口
    :param f: 入口函数
    :param name: entry名称
    :param multi_entries: 是否有多个入口函数
    :return:
    """
    if f in _func_idx_api_entries:
        logger.error('func [{0}] already registered'.format(f))
        raise RuntimeError('duplicated api entries.')
    _func_idx_api_entries[f] = name

    if name in _name_idx_api_entries:
        logger.warn('name [{0}] already registered'.format(name))
        if f != _name_idx_api_entries[name]:
            if not multi_entries:
                msg = 'name [{0}] already registered by [{1}]'.format(name, _name_idx_api_entries[name])
                logger.error(msg)
                raise ValueError(msg)
    if multi_entries:
        entries = _name_idx_api_entries.setdefault(name, [])
        entries.append(f)
    else:
        _name_idx_api_entries[name] = f


def get_api_entry_name_list():
    return _name_idx_api_entries.keys()


def get_api_entry_by_name(name):
    return _name_idx_api_entries.get(name)


def verify_request(entry_name, multi_entries=False):
    def do_verify_request(f):
        # register api entry.
        _register_api_entry(f, entry_name, multi_entries)

        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                params = {}
                params.update(request.values.items())
                params.update(request.view_args)

                logger.info("[{0}] {1}: {2}".format(entry_name, request.url, params))
                # check perm
                channel_name = params.get('channel_name')
                if channel_name is None:
                    return response.fail(msg='channel_name is needed.')

                channel = get_channel_by_name(channel_name)
                if channel is None:
                    msg = 'channel not exits: [{0}]'.format(channel_name)
                    logger.info(msg)
                    return response.fail(msg=msg)

                if channel_name not in config.TEST_CHANNELS and not channel.has_entry_perm(entry_name):
                    msg = 'channel [{0}] has no perm for entry [{1}]'.format(channel_name, entry_name)
                    logger.info(msg)
                    return response.refused(msg=msg)

                # verify sign
                sign_type = params['sign_type']
                # 这里的主要作用是验签, 只需要channel_pub_key或md5_key
                try:
                    signer = Signer('key', 'sign', channel.md5_key, None, channel.public_key)
                    if not signer.verify(params, sign_type):
                        logger.warn('sign verify error: [{0}]'.format(params))
                        msg = 'sign error.'
                        return response.refused(msg=msg)
                except Exception as e:
                    logger.exception(e)
                    msg = 'sign error.'
                    return response.refused(msg=msg)
            except Exception as e:
                logger.exception(e)
                return response.bad_request(msg=e.message)

            logger.info("[{0}] verify done.".format(entry_name))
            request.__dict__['channel'] = channel
            request.__dict__['params'] = params
            return f(*args, **kwargs)

        return wrapper

    return do_verify_request


def limit_referrer(netlocs, ex_callback=None):
    def do_limit(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                referrer = request.referrer
                parts = urlparse.urlparse(referrer)
                if parts.netloc in netlocs:
                    return f(*args, **kwargs)
            except Exception as e:
                logger.exception(e)
            if ex_callback:
                return ex_callback(*args, **kwargs)
            return response.bad_request()
        return wrapper
    return do_limit

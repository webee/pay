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


class EntryAuthError(Exception):
    def __init__(self, message=None):
        message = message or 'entry auth error.'
        message = message.encode('utf-8') if isinstance(message, unicode) else message
        super(EntryAuthError, self).__init__(message)


def _verify_channel_perm(channel, entry_name):
    if channel.name not in config.TEST_CHANNELS and not channel.has_entry_perm(entry_name):
        msg = 'channel [{0}] has no perm for entry [{1}]'.format(channel.name, entry_name)
        raise EntryAuthError(msg)


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
                    return response.fail(msg=msg)

                try:
                    _verify_channel_perm(channel, entry_name)
                except EntryAuthError as e:
                    return response.refused(msg=e.message)

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


def multi_verify_request(entry_name):
    return verify_call_perm(entry_name, multi_entries=True)


def verify_call_perm(entry_name, multi_entries=False):
    def do_verify_call(f):
        # register api entry.
        _register_api_entry(f, entry_name, multi_entries)

        @wraps(f)
        def wrapper(channel_name, *args, **kwargs):
            logger.info("[{0}]: [{1}]".format(entry_name, channel_name))

            channel = get_channel_by_name(channel_name)
            if channel is None:
                msg = 'channel not exits: [{0}]'.format(channel_name)
                raise EntryAuthError(msg=msg)

            _verify_channel_perm(channel, entry_name)

            logger.info("[{0}] verify done.".format(entry_name))
            return f(channel_name, *args, **kwargs)

        return wrapper

    return do_verify_call


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


def prepay_entry(source):
    from api_x.zyt.biz.models import Transaction

    def entry(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            res = f(*args, **kwargs)
            if isinstance(res, Transaction):
                tx = res
                # FIXME: this is prepay_id
                hashed_sn = tx.sn_with_expire_hash
                # FIXME: 不直接返回pay_url, 修改pay_client, pay_url作为web支付方式在客户端确定
                # 目前主要是兼容活动平台
                checkout_url = config.CHECKOUT_URL.format(sn=hashed_sn)
                return response.success(sn=hashed_sn, pay_url=checkout_url)
            return res
        return wrapper
    return entry


def payment_entry(f):
    from api_x.zyt.biz.models import Transaction

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            params = request.view_args
            hashed_sn = params.get('sn')
            tx, expire_hash = Transaction.get_tx_from_hashed_sn(hashed_sn)
            if tx is None:
                # 没找到
                return response.not_found()
            if not tx.check_expire_hash(expire_hash):
                # 过期
                return response.expired(msg='expired, please retry request pay.')

            return f(tx, *args, **kwargs)
        except Exception as e:
            logger.exception(e)
        # 异常
        return response.bad_request()
    return wrapper

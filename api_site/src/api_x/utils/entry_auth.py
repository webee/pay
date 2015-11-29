# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import wraps
import urlparse

from flask import request
from api_x.utils import response, ds
from pytoolbox.util.log import get_logger
from pytoolbox.util.sign import Signer
from api_x.zyt.user_mapping import get_channel_by_name
from api_x.config import etc as config
import types

logger = get_logger(__name__)


class ApiEntry:
    def __init__(self, entry=None):
        self.entry = entry

    def __eq__(self, other):
        return isinstance(other, ApiEntry) and other.entry == self.entry

    def __hash__(self):
        return hash(self.entry)

    @property
    def value(self):
        if isinstance(self.entry, types.FunctionType):
            return self.entry.__module__ + '.' + self.entry.func_name
        return repr(self.entry)

    def __repr__(self):
        return "<ApiEntry: %r>" % (self.value,)

_api_entry_path_map = {}
_api_entry_trie = ds.Trie()


def _do_register_api_entry(entry, path):
    """
    注册api入口
    :param entry:
    :param path:
    :return:
    """
    if entry in _api_entry_path_map and _api_entry_path_map[entry] != path:
        msg = 'api entry [{0}] already registered to [{1}] != [{2}]'.format(entry, _api_entry_path_map[entry], path)
        logger.error(msg)
        raise RuntimeError(msg)

    if path in _api_entry_trie:
        _entry = _api_entry_path_map[path]
        if _entry != entry:
            msg = 'path [{0}] already registered by [{1}] != [{2}]'.format(path, _entry, entry)
            logger.error(msg)
            raise RuntimeError(msg)

    _api_entry_trie[path] = entry
    _api_entry_path_map[entry] = path


def _register_api_entry(f, _entry_name):
    """
    注册api入口
    :param f: 入口函数
    :param _entry_name: entry路径
    :return:
    """
    entry_path = _to_entry_path(_entry_name)
    _do_register_api_entry(ApiEntry(f), entry_path)
    return entry_path


def get_api_entry_trie():
    return _api_entry_trie.clone()


def get_api_entry_by_path(path):
    return _api_entry_trie[path]


class EntryAuthError(Exception):
    def __init__(self, message=None):
        message = message or 'entry auth error.'
        message = message.encode('utf-8') if isinstance(message, unicode) else message
        super(EntryAuthError, self).__init__(message)


def _verify_channel_perm(channel, entry_path):
    if channel.name not in config.TEST_CHANNELS and not channel.has_entry_perm(entry_path):
        msg = 'channel [{0}] has no perm for entry [{1}]'.format(channel.name, entry_path)
        raise EntryAuthError(msg)


def verify_request(_entry_name):
    def do_verify_request(f):
        # register api entry.
        entry_path = _register_api_entry(f, _entry_name)

        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                params = {}
                params.update(request.values.items())
                params.update(request.view_args)

                logger.info("[{0}] {1}: {2}".format(entry_path, request.url, params))
                # check perm
                channel_name = params.get('channel_name')
                if channel_name is None:
                    return response.fail(msg='channel_name is needed.')

                channel = get_channel_by_name(channel_name)
                if channel is None:
                    msg = 'channel not exits: [{0}]'.format(channel_name)
                    return response.fail(msg=msg)

                try:
                    _verify_channel_perm(channel, entry_path)
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

            logger.info("[{0}] verify done.".format(entry_path))
            request.__dict__['channel'] = channel
            request.__dict__['params'] = params
            return f(*args, **kwargs)

        return wrapper

    return do_verify_request


def _to_entry_path(name):
    return tuple(n for n in name) if isinstance(name, (list, tuple)) else (name,)


class GroupEntry:
    def __init__(self, name):
        """
        :param name: str/unicode, list or tuple.
        :return:
        """
        self.path = _to_entry_path(name)

    def _get_path(self, _entry_name):
        entry_path = _to_entry_path(_entry_name)
        return self.path + entry_path

    def verify_request(self, _entry_name):
        return verify_request(self._get_path(_entry_name))

    def verify_call_perm(self, _entry_name):
        return verify_call_perm(self._get_path(_entry_name))


def verify_call_perm(_entry_name):
    def do_verify_call(f):
        # register api entry.
        entry_path = _register_api_entry(f, _entry_name)

        @wraps(f)
        def wrapper(channel_name, *args, **kwargs):
            logger.info("[{0}]: [{1}]".format(entry_path, channel_name))

            channel = get_channel_by_name(channel_name)
            if channel is None:
                msg = 'channel not exits: [{0}]'.format(channel_name)
                raise EntryAuthError(msg=msg)

            _verify_channel_perm(channel, entry_path)

            logger.info("[{0}] verify done.".format(entry_path))
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

# coding=utf-8
from __future__ import unicode_literals

from .models import EventType
from .bookkeep import bookkeeping
from . import NAME as ZYT_NAME
from pytoolbox.util.dbs import transactional


@transactional
def transfer_frozen(sn, from_user_id, to_user_id, amount):
    """转账冻结金额"""
    return [bookkeeping(EventType.TRANSFER_OUT_FROZEN, sn, from_user_id, ZYT_NAME, amount),
            bookkeeping(EventType.TRANSFER_IN, sn, to_user_id, ZYT_NAME, amount)]


@transactional
def transfer(sn, from_user_id, to_user_id, amount):
    """转账"""
    return [bookkeeping(EventType.TRANSFER_OUT, sn, from_user_id, ZYT_NAME, amount),
            bookkeeping(EventType.TRANSFER_IN, sn, to_user_id, ZYT_NAME, amount)]

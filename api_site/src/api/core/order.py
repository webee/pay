# -*- coding: utf-8 -*-
from ._dba import create_trade_order, update_trade_order_state
from pytoolbox.util.enum import enum

_ORDER_TYPE = enum(PAY='PAY', REFUND='REFUND', WITHDRAW='WITHDRAW', TRANSFER='TRANSFER')


def generate_pay_order(source_id, from_account_id, to_account_id, amount, state, info):
    return _generate_order(_ORDER_TYPE.PAY, source_id, from_account_id, to_account_id, amount, state, info)


def generate_refund_order(source_id, from_account_id, to_account_id, amount, state, info):
    return _generate_order(_ORDER_TYPE.REFUND, source_id, from_account_id, to_account_id, amount, state, info)


def generate_transfer_order(source_id, from_account_id, to_account_id, amount, state, info):
    return _generate_order(_ORDER_TYPE.TRANSFER, source_id, from_account_id, to_account_id, amount, state, info)


def update_order_state(source_id, state):
    update_trade_order_state(source_id, state)


def _generate_order(type, source_id, from_account_id, to_account_id, amount, state, info):
    return create_trade_order(type, source_id, from_account_id, to_account_id, amount, state, info)

# -*- coding: utf-8 -*-
from ._dba import create_trade_order, update_trade_order_state, find_trade_order_by_source_id, list_trade_orders, \
    count_all_trade_orders
from pytoolbox.util.enum import enum

_ORDER_TYPE = enum(PAY='PAY', REFUND='REFUND', WITHDRAW='WITHDRAW', TRANSFER='TRANSFER')


def generate_pay_order(source_id, from_account_id, to_account_id, amount, state, info):
    return _find_or_create_order(_ORDER_TYPE.PAY, source_id, from_account_id, to_account_id, amount, state, info)


def generate_refund_order(source_id, from_account_id, to_account_id, amount, state, info):
    return _find_or_create_order(_ORDER_TYPE.REFUND, source_id, from_account_id, to_account_id, amount, state, info)


def generate_transfer_order(source_id, from_account_id, to_account_id, amount, state, info):
    return _find_or_create_order(_ORDER_TYPE.TRANSFER, source_id, from_account_id, to_account_id, amount, state, info)


def generate_withdraw_order(source_id, account_id, amount, state, info):
    return _find_or_create_order(_ORDER_TYPE.WITHDRAW, source_id, account_id, None, amount, state, info)


def update_order_state(source_id, state):
    update_trade_order_state(source_id, state)


def _find_or_create_order(type, source_id, from_account_id, to_account_id, amount, state, info):
    order = find_trade_order_by_source_id(source_id)
    if order:
        return order.id
    return create_trade_order(type, source_id, from_account_id, to_account_id, amount, state, info)


def list_orders(account_id, category, page_no, page_size, keyword):
    count = count_all_trade_orders(account_id, category, keyword)

    offset = (page_no - 1) * page_size
    raw_orders = list_trade_orders(account_id, category, offset, page_size, keyword)

    formatted_orders = []
    for order in raw_orders:
        income_ratio = 1 if order['to_account_id'] == account_id else -1
        formatted_orders.append({
            'id': order.id,
            'type': order.type,
            'amount': float(order.amount) * income_ratio,
            'info': order.info,
            'created_on': order.created_on
        })
    return count, formatted_orders

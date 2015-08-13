# coding=utf-8
from __future__ import unicode_literals

from pub_site import pay_client

TRADE_TYPE_MSG = {
    'PAY': '支付',
    'REFUND': '退款',
    'PREPAID': '充值',
    'TRANSFER': '转账'
}


def list_trade_orders(uid, category, page_no, page_size, keyword):
    data = pay_client.list_trade_orders(uid, category, page_no, page_size, keyword)
    records = data['records']
    for record in records:
        record['type'] = TRADE_TYPE_MSG[record['type']]

    return data['total'], records
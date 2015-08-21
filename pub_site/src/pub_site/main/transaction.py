# coding=utf-8
from __future__ import unicode_literals

from pub_site import pay_client


TX_TYPE_MSG = {
    'PAYMENT:FROM': '支付付款',
    'PAYMENT:TO': '支付收款',
    'PAYMENT:GUARANTEE': '支付担保',
    'REFUND:FROM': '支付退款',
    'REFUND:TO': '接受退款',
    'REFUND:GUARANTEE': '退款担保',
    'WITHDRAW:FROM': '提现',
    'PREPAID:TO': '充值',
    'TRANSFER:FROM': '转账付款',
    'TRANSFER:TO': '转账收款',
}

TX_STATE_MSG = {
    'PAYMENT:CREATED': '等待支付',
    'PAYMENT:SECURED': '支付完成|等待确认',
    'PAYMENT:FAILED': '支付失败',
    'PAYMENT:SUCCESS': '交易完成',
    'PAYMENT:REFUNDED': '已退款',
    'PAYMENT:REFUNDING': '退款中',
    'REFUND:CREATED': '正在处理',
    'REFUND:FAILED': '退款失败',
    'REFUND:SUCCESS': '交易完成',
    'WITHDRAW:PROCESSING': '正在处理',
    'WITHDRAW:FAILED': '提现失败',
    'WITHDRAW:SUCCESS': '交易完成',
}


def query_transactions(uid, role, page_no, page_size, keyword):
    data = pay_client.query_transactions(uid, role, page_no, page_size, keyword)
    txs = [_process_tx(tx) for tx in data['transactions']]

    return data['total'], data['transactions']


def _process_tx(tx):
    tx['is_failed'] = tx['state'] == 'FAILED'

    tx['state'] = TX_STATE_MSG['%s:%s' % (tx['type'], tx['state'])]
    tx['type'] = TX_TYPE_MSG['%s:%s' % (tx['type'], tx['role'])]

    return tx

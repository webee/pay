# coding=utf-8
from __future__ import unicode_literals

from pub_site import pay_client


TX_TYPE_MSG = {
    'PAYMENT': '支付',
    'REFUND': '退款',
    'WITHDRAW': '提现',
    'PREPAID': '充值',
    'TRANSFER': '转账',
}

TX_STATE_MSG = {
    'PAYMENT:CREATED': '等待支付',
    'PAYMENT:SECURED': '支付完成|等待确认',
    'PAYMENT:FAILED': '支付失败',
    'PAYMENT:SUCCESS': '支付成功',
    'PAYMENT:REFUNDED': '已退款',
    'PAYMENT:REFUNDING': '退款中',
    'REFUND:CREATED': '正在处理',
    'REFUND:FAILED': '退款失败',
    'REFUND:SUCCESS': '退款成功',
    'WITHDRAW:PROCESSING': '正在处理',
    'WITHDRAW:FAILED': '提现失败',
    'WITHDRAW:SUCCESS': '提现成功',
}


def query_transactions(uid, role, page_no, page_size, keyword):
    data = pay_client.query_transactions(uid, role, page_no, page_size, keyword)
    txs = [_process_tx(tx) for tx in data['transactions']]

    return data['total'], data['transactions']


def _process_tx(tx):
    tx['is_failed'] = tx['state'] == 'FAILED'
    tx['state'] = TX_STATE_MSG['%s:%s' % (tx['type'], tx['state'])]
    tx['type'] = TX_TYPE_MSG[tx['type']]

    return tx

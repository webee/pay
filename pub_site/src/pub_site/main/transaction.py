# coding=utf-8
from __future__ import unicode_literals

from pub_site import pay_client


TX_TYPE_MSG = {
    'PAYMENT:TX_FROM': '交易付款',
    'PAYMENT:FROM': '付款',
    'PAYMENT:TO': '支付收款',
    'PAYMENT:GUARANTEE': '支付担保',
    'REFUND:FROM': '退款',
    'REFUND:TO': '退款',
    'REFUND:TX_TO': '交易退款',
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
    'PREPAID:CREATED': '等待支付',
    'PREPAID:FAILED': '支付失败',
    'PREPAID:SUCCESS': '支付完成',
    'REFUND:PROCESSING': '正在处理',
    'REFUND:BLOCK': '等待处理',
    'REFUND:FAILED': '退款失败',
    'REFUND:SUCCESS': '交易完成',
    'WITHDRAW:PROCESSING': '正在处理',
    'WITHDRAW:FAILED': '提现失败',
    'WITHDRAW:SUCCESS': '交易完成',
    'TRANSFER:CREATED': '等待支付',
    'TRANSFER:FAILED': '转账失败',
    'TRANSFER:SUCCESS': '交易完成',
}

# TODO: 直接从接口获取
TX_VAS_MSG = {
    '': '-',
    'LIANLIAN_PAY': '连连支付',
    'ZYT': '自游通',
    'TEST_PAY': '测试支付',
    'ALI_PAY': '支付宝',
    'WX1227342102': '微信支付(服务号)',
    'WX1279128101': '微信支付(滑雪达人)',
}

TX_CHANNEL_MSG = {
    'lvye_huodong': '绿野活动',
    'lvye_pay_test': '自游通测试',
    'lvye_pay_site': '自游通网站',
    'zyt_sample': '自游通sample系统',
    'lvye_skiing': '绿野滑雪',
    'lvye_lvxing': '绿野旅行',
    'lvye_pay_admin': '绿野支付管理系统',
    'lvye_corp_pay_site': '绿野公司用户操作平台',
    }


def query_transactions(uid, role, page_no, page_size, vas_name, keyword):
    data = pay_client.list_transactions(uid, role, page_no, page_size, vas_name, keyword)
    if data is None:
        return 0, []

    txs = [_process_tx(tx) for tx in data['txs']]

    return data['total'], txs


def _process_tx(tx):
    tx['is_failed'] = tx['state'] == 'FAILED'
    tx['is_created'] = tx['state'] == 'CREATED'

    tx['state'] = TX_STATE_MSG['%s:%s' % (tx['type'], tx['state'])]
    tx['type'] = TX_TYPE_MSG['%s:%s' % (tx['type'], tx['role'])]
    tx['vas'] = TX_VAS_MSG[tx['vas_name']]
    tx['channel'] = TX_CHANNEL_MSG[tx['channel_name']]

    return tx

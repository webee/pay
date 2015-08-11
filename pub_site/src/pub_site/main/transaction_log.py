# coding=utf-8
from __future__ import unicode_literals

from pub_site import pay_client

TRADE_TYPE_MSG = {
    'WITHDRAW:FROZEN': '提现',
    'WITHDRAW:FAILED': '提现-退款',
    'PAY': '支付',
    'PREPAID': '充值',
    'TRANSFER': '转账'
}


def cash_records(uid, q, side, tp, page_no=1, page_size=20):
    data = pay_client.get_user_cash_records(uid, q, side, tp, page_no, page_size)
    count, records, record_infos = data['count'], data['records'], data['record_infos']
    for record in records:
        source_type = record['source_type']
        source_id = record['source_id']
        info = record_infos[source_id]
        record['state'] = '已完成'
        record['type'] = TRADE_TYPE_MSG[source_type]
        if source_type == 'WITHDRAW:FROZEN':
            if info['state'] == 'FROZEN':
                record['state'] = '处理中'
            elif info['state'] == 'FAILED':
                record['state'] = '已失败'
    return count, records, record_infos

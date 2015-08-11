# coding=utf-8
from __future__ import unicode_literals
from flask import request, render_template
from flask.ext.login import login_required, current_user
from . import main_mod as mod
from pub_site import pay_client
from .user import format_account_user
from ..constant import TradeType


@mod.route('/', methods=['GET'])
@login_required
def index():
    from pub_site.constant import SOURCE_MESSAGES

    uid = current_user.user_id
    balance = pay_client.get_user_balance(uid)
    records, record_info = pay_client.get_user_cash_records(uid)
    for record in records:
        source_type = record['source_type']
        source_id = record['source_id']
        info = record_info[source_id]
        if source_type == 'WITHDRAW:FROZEN':
            record['opposite'] = '银行'
            record['type'] = '提现'
            record['trade_info'] = '提现到银行卡'
        elif source_type == 'WITHDRAW:FAILED':
            record['opposite'] = '自游通'
            record['type'] = '提现-退款'
            record['trade_info'] = '提现失败'
        elif source_type == 'PAY':
            record['opposite'] = info['payer_account_id']
            record['type'] = '收款'
            record['trade_info'] = '支付收款'
        elif source_type == 'PREPAID':
            record['opposite'] = 'test'
            record['type'] = '充值'
            record['trade_info'] = '充值'
        elif source_type == 'TRANSFER':
            if record['account_id'] == info['payer_account_id']:
                record['opposite'] = format_account_user(info['payee_account_id'])
            else:
                record['opposite'] = format_account_user(info['payer_account_id'])
            record['type'] = '转账'
            record['trade_info'] = '转账'

    res = {
        'balance': balance,
        'records': records,
        'record_info': record_info,
    }
    return render_template('main/index.html', res=res, source_messages=SOURCE_MESSAGES)


@mod.route('/trade/<int:id>', methods=['GET'])
@login_required
def trade_detail(id):
    trade = {"id": id, "type": TradeType.WITHDRAW}
    return render_template('main/trade-detail.html', trade=trade)
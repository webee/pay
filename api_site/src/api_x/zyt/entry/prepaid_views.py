# coding=utf-8
from __future__ import unicode_literals

from flask import request, render_template
from . import biz_entry_mod as mod
from api_x.constant import VirtualAccountSystemType, TransactionType


@mod.route('/prepaid', methods=['GET'])
def prepaid():
    data = request.values
    user_id = data['user_id']
    amount = data['amount']

    return render_template('prepaid.html', user_id=user_id, amount=amount, vas=VirtualAccountSystemType)


@mod.route("/prepaid_by/<vas_name>", methods=["GET"])
def prepaid_by(vas_name):
    from api_x.zyt.evas import test_pay

    """充值入口"""
    data = request.values
    user_id = data['user_id']
    amount = data['amount']

    if vas_name == test_pay.NAME:
        from api_x.zyt.biz.utils import generate_sn
        return test_pay.pay(TransactionType.PREPAID, user_id, generate_sn(user_id), '账户充值', amount)
    return render_template('info.html', title='错误', msg='暂不支持此支付方式')

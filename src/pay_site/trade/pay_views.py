# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from datetime import datetime
from flask import request, redirect, url_for, jsonify
from tools.dbi import from_db, require_transaction_context
from tools.dbi import transactional
from tools.mylog import get_logger
from . import trade_mod as mod
import zgt.service as zgt
from .utils import format_string
from service import get_or_create_account, gen_transaction_id

logger = get_logger(__name__)


@mod.route('/pay/', methods=['GET', 'POST'])
def pay():
    """支付接口
    :return:
    """
    # TODO: 加密接口数据
    data = request.args
    if request.method == 'POST':
        data = request.form

    client_id = format_string(data.get('client_id'))
    order_id = format_string(data.get('order_id'))

    product_name = format_string(data.get('product_name'))
    product_category = format_string(data.get('product_category'))
    product_desc = format_string(data.get('product_desc'))

    user_source = format_string(data.get('user_source'))
    user_id = format_string(data.get('user_id'))

    to_account_id = format_string(data.get('to_account_id'))
    amount = float(format_string(data.get('amount', '0')))

    # TODO: check parameters.
    # requires, account exists.
    #

    # 新建普通用户
    account = get_or_create_account(user_source, user_id)
    payment_id = gen_transaction_id(account['id'])

    payment_fields = {'client_id': client_id, 'order_id': order_id,
                      'product_name': product_name, 'product_category': product_category, 'product_desc': product_desc,
                      'id': payment_id,
                      'account_id': account['id'], 'to_account_id': to_account_id, 'amount': amount}
    create_payment(payment_fields)
    payment = from_db().get('select * from payment where id=%(id)s', id=payment_id)

    pay_callback_url = url_for('trade.pay_callback', _external=True)
    pay_web_callback_url = url_for('trade.pay_web_callback', _external=True)
    logger.info("pay_callback_url: %s", pay_callback_url)

    request_params = {
        'requestid': payment['id'],
        'amount': str(payment['amount']),
        'assure': '0',
        'productname': payment['product_name'],
        'productcat': payment['product_category'],
        'productdesc': payment['product_desc'],
        'divideinfo': '',
        'callbackurl': pay_callback_url,
        'webcallbackurl': pay_web_callback_url,
        'bankid': '',
        'period': '',
        'memo': '',
        'payproducttype': 'ONEKEY',
        'userno': payment['account_id'],
        'ip': '',
        'cardname': '',
        'idcard': '',
        'bankcardnum': ''
    }

    request_result = zgt.payment_request(request_params)

    code = zgt.format_string(request_result.get('code'))
    msg = zgt.format_string(request_result.get('msg'))
    custom_error = zgt.format_string(request_result.get('customError'))
    payurl = zgt.format_string(request_result.get('payurl'))

    # TODO: 跳转到错误页面
    if custom_error != "":
        return jsonify(customError=custom_error)
    elif code != "1":
        return jsonify(code=code, msg=msg)

    # 成功
    if payurl != "":
        return redirect(payurl)

    # 无卡直连成功
    # 跳转到支付成功页面
    # TODO: 添加相应参数
    return redirect(url_for("main.pay_web_callback", param=1))


@transactional
def create_payment(fields):
    return from_db().insert('payment', **fields)


@mod.route('/pay_callback/', methods=['GET', 'POST'])
def pay_callback():
    """付款后台回调
    :return:
    """
    data = request.args
    if request.method == 'POST':
        data = request.args.form
    data = data.get('data')

    hmac_encryption_order = ['customernumber', 'requestid', 'code', 'notifytype', 'externalid', 'amount',
                             'cardno', 'bankcode']
    result = zgt.parse_data_from_yeepay(data, hmac_encryption_order)

    # TODO: check result, notifytype==SERVER, amount.
    #

    code = result['code']
    logger.info(str(result))
    if code == "1":
        # success
        payment_id = result['requestid']
        payment = from_db().get("select * from payment where id=%(id)s", id=payment_id)
        if payment is not None:
            with require_transaction_context():
                from_db().execute('update payment set sucess=1, yeepay_transaction_id=%(externalid)s, transaction_ended_on=current_timestamp() where id=%(id)s',
                                  externalid=result['externalid'], id=payment['id'])
    return "SUCCESS"


@mod.route('/pay_web_callback/', methods=['GET', 'POST'])
def pay_web_callback():
    """付款前台回调
    :return:
    """
    data = request.args.get('data')
    if request.method == 'POST':
        data = request.args.form
    data = data.get('data')

    result = {}
    if data:
        hmac_encryption_order = ['customernumber', 'requestid', 'code', 'notifytype', 'externalid', 'amount',
                                 'cardno', 'bankcode']
        result = zgt.parse_data_from_yeepay(data, hmac_encryption_order)

    return jsonify(result)

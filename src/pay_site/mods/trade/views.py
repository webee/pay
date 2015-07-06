# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

import logging
from datetime import datetime
from flask import request, redirect, url_for, jsonify
from tools.dbi import from_db
from tools.dbi import transactional
from tools.mylog import get_logger
from . import trade_mod as mod
import zgt.service as zgt


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

    source_channel = zgt.format_string('source_channel')
    source_order_id = zgt.format_string('source_order_id')
    source_user_id = zgt.format_string(data.get('source_user_id'))
    source_account = zgt.format_string(data.get('source_account'))
    amount = float(zgt.format_string(data.get('amount', '0')))
    to_account = zgt.format_string(data.get('to_account'))
    product_name = zgt.format_string(data.get('product_name'))
    product_cat = zgt.format_string(data.get('product_cat'))
    product_desc = zgt.format_string(data.get('product_desc'))
    trade_type = 1
    trade_serial_no = "ZGTPAY" + datetime.now().strftime("%y%m%d_%H%M%S%f")
    status = "INIT"

    # TODO: check parameters.
    # requires, account exists.

    record = {'source_channel': source_channel, 'source_order_id': source_order_id,
              'source_user_id': source_user_id, 'source_account': source_account,
              'amount': amount, 'to_account': to_account,
              'trade_type': trade_type, 'trade_serial_no': trade_serial_no, 'status': status,
              'product_name': product_name, 'product_cat': product_cat, 'product_desc': product_desc}
    trade_id = create_trade_record(record)
    trade_record = from_db().get('select * from trade_records where id=%(id)s', id=trade_id)

    # TODO: 配置此地址
    host_url = request.host_url.strip('/')
    pay_callback_url = host_url + url_for('trade.pay_callback')
    pay_web_callback_url = host_url + url_for('trade.pay_web_callback')

    request_params = {
        'requestid': trade_record['trade_serial_no'],
        'amount': str(trade_record['amount']),
        'assure': '0',
        'productname': trade_record['product_name'],
        'productcat': trade_record['product_cat'],
        'productdesc': trade_record['product_desc'],
        'divideinfo': '',
        'callbackurl': pay_callback_url,
        'webcallbackurl': pay_web_callback_url,
        'bankid': '',
        'period': '',
        'memo': '',
        'payproducttype': 'ONEKEY',
        'userno': gen_userno(trade_record['source_account'], trade_record['source_user_id']),
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


def gen_userno(source_account, from_user):
    import hashlib
    md = hashlib.md5(source_account+from_user)
    return md.hexdigest()[:30]


@transactional
def create_trade_record(record):
    return from_db().insert('pay_trade_records', returns_id=True, **record)


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

    code = result['code']
    logger.info(str(result))
    if code == "1":
        # success
        trade_serial_no = result['requestid']
        trade_record = from_db().get("select * from trade_records where trade_serial_no=%(trade_serial_no)s",
                                     trade_serial_no=trade_serial_no)
        if trade_record:
            trade_record = {k: v for k, v in trade_record.items() if k != 'id'}
            trade_record['status'] = "SUCCESS"

            trade_id = create_trade_record(trade_record)
        return "SUCCESS"
    return ""


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

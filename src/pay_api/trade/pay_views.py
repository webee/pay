# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

import urllib

from flask import request, url_for, jsonify, current_app
from tools.dbi import from_db, require_transaction_context
from tools.dbi import transactional
from tools.mylog import get_logger
from . import trade_mod as mod
import zgt.service as zgt
from tools.utils import format_string, to_int, to_float
from service import get_or_create_account, gen_transaction_id
import requests

logger = get_logger(__name__)


@mod.route('/pay/', methods=['GET', 'POST'])
def pay():
    """支付接口
    :return:
    """
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
    amount = to_float(format_string(data.get('amount')))

    callback = format_string(data.get('callback'))
    web_callback = format_string(data.get('web_callback'))

    # check parameters.
    client_info = from_db().get("select * from client_info where client_id=%(client_id)s", client_id=client_id)
    if client_info is None:
        return jsonify(ret=False, code=600, msg="客户不存在: %s" % client_id)
    account = from_db().get("select * from account where id=%(id)s", id=to_int(to_account_id))
    if not account:
        return jsonify(ret=False, code=601, msg="账号不存在: %s" % to_account_id)
    if amount <= 0:
        return jsonify(ret=False, code=602, msg="金额错误")

    # 新建普通用户
    account = get_or_create_account(user_source, user_id)
    payment_id = gen_transaction_id(account['id'])

    payment_fields = {'client_id': client_id, 'order_id': order_id,
                      'product_name': product_name, 'product_category': product_category, 'product_desc': product_desc,
                      'id': payment_id,
                      'account_id': account['id'], 'to_account_id': to_account_id, 'amount': amount,
                      'callback_url': callback}
    create_payment(payment_fields)
    payment = from_db().get('select * from payment where id=%(id)s', id=payment_id)

    host_url = current_app.config.get('HOST_URL')
    pay_callback_url = host_url + url_for('trade.pay_callback') + '?' + urllib.urlencode({'d': payment_id})
    pay_web_callback_url = web_callback
    logger.info("pay_callback_url: %s", pay_callback_url)
    logger.info("pay_web_callback_url: %s", pay_web_callback_url)

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
    # FIXME: 目前只使用ONEKEY方式支付
    logger.info('request_params: %s' % repr(request_params))

    request_result = zgt.payment_request(request_params)

    code = zgt.format_string(request_result.get('code'))
    msg = zgt.format_string(request_result.get('msg'))
    custom_error = zgt.format_string(request_result.get('customError'))
    payurl = zgt.format_string(request_result.get('payurl'))

    # TODO: 跳转到错误页面
    if custom_error != "":
        logger.error(custom_error)
        return jsonify(ret=False, code=1000, msg="系统错误")
    elif code != "1":
        logger.error("yeepay error: %s, %s" % (code, msg))
        return jsonify(ret=False, code=1000, msg="系统错误")

    if payurl != "":
        return jsonify(ret=True, payurl=payurl)
    return jsonify(ret=False, code=1000, msg="系统错误")


@transactional
def create_payment(fields):
    return from_db().insert('payment', **fields)


@mod.route('/pay_callback/', methods=['GET', 'POST'])
def pay_callback():
    """付款后台回调
    :return:
    """
    payment_id = format_string(request.args.get('d'))

    data = request.args
    if request.method == 'POST':
        data = request.args.form
    data = data.get('data')

    hmac_sign_order = ['customernumber', 'requestid', 'code', 'notifytype', 'externalid', 'amount',
                       'cardno', 'bankcode']
    result = zgt.parse_data_from_yeepay(data, hmac_sign_order)

    logger.info("callback result: %s" % str(result))

    client_callback = None
    code = result['code']
    ret = None
    if code != "1":
        # 失败
        msg = result.get('msg', '')
        logger.info("支付失败, %s" % msg)
        ret = {'ret': False, 'payment_id': payment_id, 'msg': msg}
        payment = from_db().get("select * from payment where id=%(id)s", id=payment_id)
        if payment is not None:
            client_callback = payment['callback_url']
    else:
        # success
        notifytype = result['notifytype']
        if notifytype != "SERVER":
            logger.warn("need notifytype SERVER, get %s" % notifytype)
        actual_amount = float(result['amount'])

        payment_id = result['requestid']
        payment = from_db().get("select * from payment where id=%(id)s", id=payment_id)
        if payment is not None:
            with require_transaction_context():
                from_db().execute('update payment set success=1, actual_amount=%(actual_amount)s, yeepay_transaction_id=%(externalid)s, transaction_ended_on=current_timestamp() where id=%(id)s',
                                  externalid=result['externalid'], actual_amount=actual_amount, id=payment['id'])
            ret = {'ret': True, 'order_id': payment['order_id'],
                   'payment_id': payment_id, 'amount': actual_amount}
            client_callback = payment['callback_url']
    # call client.
    # TODO: 设计更可靠的方式
    req = requests.post(client_callback, ret)
    if req.status_code != 200 and not req.content.startswith('SUCCESS'):
        logger.info("client callback success.")
        # try more.
        pass

    return "SUCCESS"


@mod.route('/query_pay/', methods=['GET', 'POST'])
def query_pay():
    """支付查询接口
    :return:
    """
    # TODO: 加密接口数据
    data = request.args
    if request.method == 'POST':
        data = request.form

    payment_id = format_string(data.get('payment_id'))

    request_params = {
        'requestid': payment_id
    }

    request_result = zgt.payment_query(request_params)

    return jsonify(request_result)

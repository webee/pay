# coding=utf-8
from __future__ import unicode_literals
from api_x.utils import response
from api_x.zyt.biz import payment
from api_x.constant import TransactionState
from api_x.zyt.biz.transaction.dba import get_tx_by_sn

from flask import request, render_template, url_for, abort, redirect
from api_x.zyt.user_mapping import get_or_create_account_user
from api_x.config import etc as config
from api_x.zyt.user_mapping import get_channel_by_name
from . import biz_entry_mod as mod
from pytoolbox.util.log import get_logger
from api_x.utils.entry_auth import verify_request
from api_x.zyt.biz.models import PaymentType


logger = get_logger(__name__)


@mod.route('/prepay', methods=['POST'])
@verify_request('prepay')
def prepay():
    data = request.values
    channel = request.channel
    payer_user_id = data['payer_user_id']
    payee_user_id = data['payee_user_id']
    order_id = data['order_id']
    product_name = data['product_name']
    product_category = data['product_category']
    product_desc = data['product_desc']
    amount = data['amount']
    client_callback_url = data['client_callback_url']
    client_notify_url = data['client_notify_url']
    payment_type = data['payment_type']

    # check
    if payment_type not in [PaymentType.DIRECT, PaymentType.GUARANTEE]:
        return response.fail(msg="payment_type [{0}] not supported.".format(payment_type))

    payer_id = get_or_create_account_user(channel.user_domain_id, payer_user_id)
    payee_id = get_or_create_account_user(channel.user_domain_id, payee_user_id)

    try:
        payment_record = payment.find_or_create_payment(channel, payment_type, payer_id, payee_id, order_id,
                                                        product_name, product_category, product_desc, amount,
                                                        client_callback_url, client_notify_url)
        pay_url = config.HOST_URL + url_for('biz_entry.cashier_desk', sn=payment_record.sn)

        return response.success(sn=payment_record.sn, pay_url=pay_url)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)


@mod.route('/cashier_desk/<sn>', methods=['GET'])
def cashier_desk(sn):
    """支付收银台入口"""
    tx = get_tx_by_sn(sn)
    if tx is None:
        abort(404)
    if tx.state != TransactionState.CREATED:
        return render_template("info.html", msg="该订单已支付")

    if len(config.Biz.ACTIVATED_EVAS) == 1:
        # 只有一种支付方式，则直接跳转到支付页面
        vas_name = config.Biz.ACTIVATED_EVAS[0]
        return redirect(url_for('.pay', sn=sn, vas_name=vas_name))
    return render_template("cashier_desk.html", root_url=config.HOST_URL, tx=tx, vases=config.Biz.ACTIVATED_EVAS)


@mod.route("/pay/<sn>/<vas_name>", methods=["GET"])
def pay(sn, vas_name):
    """支付入口"""
    from . import payment

    tx = get_tx_by_sn(sn)
    if tx is None:
        response.not_found(msg='tx sn=[{0}] not fund.'.format(sn))
    if tx.state != TransactionState.CREATED:
        return render_template("info.html", msg="该订单已支付")

    if vas_name not in config.Biz.ACTIVATED_EVAS:
        # 不支持此支付方式
        abort(404)

    return payment.pay(vas_name, tx)


@mod.route("/pay/result/<sn>/<vas_name>", methods=["GET"])
def pay_result(sn, vas_name):
    data = request.data
    code = data['code']
    vas_sn = data['vas_sn']

    msg = "支付成功" if code == 0 else "支付失败"
    return render_template('pay_result.html', title='支付结果', sn=sn, vas_name=vas_name, vas_sn=vas_sn, msg=msg)


@mod.route('/pay/guarantee_payment/confirm', methods=['POST'])
@verify_request('confirm_guarantee_payment')
def confirm_guarantee_payment():
    from api_x.utils import response
    data = request.values
    channel_name = data['channel_name']
    order_id = data['order_id']

    channel = get_channel_by_name(channel_name)
    if channel is None:
        return response.fail(msg='channel not exits: [{0}]'.format(channel_name))

    try:
        payment.confirm_payment(channel, order_id)
        return response.success()
    except Exception as e:
        logger.exception(e)
        return response.bad_request(msg=e.message)

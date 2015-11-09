# coding=utf-8
from __future__ import unicode_literals

from api_x.utils.entry_auth import payment_entry, verify_request
from api_x.constant import PaymentTxState, TransactionType
from api_x.utils import response
from api_x.zyt.evas.payment import gen_payment_entity
from api_x.zyt.vas import get_pay_notify_handle, NotifyType
from . import biz_entry_mod as mod
from flask import request, render_template
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


@mod.route("/payment/<sn>/result", methods=["GET"])
@payment_entry
def pay_result(tx, sn):
    return response.success(state=tx.state)


@mod.route("/payment/<sn>/<payment_scene>/info", methods=["GET"])
@payment_entry
def info(tx, sn, payment_scene):
    return query_info(tx, payment_scene)


@mod.route("/payment/<sn>/<payment_scene>/<vas_name>/param", methods=["GET"])
@payment_entry
def params(tx, sn, payment_scene, vas_name):
    return prepare_params(tx, payment_scene, vas_name)


def query_info(tx, payment_scene):
    from api_x.zyt.evas.payment import infos

    # TODO: log to db.
    logger.info("[PAYMENT INFO] {0}, {1}, {2}".format(payment_scene, tx.type, tx.sn))
    payment_entity = gen_payment_entity(tx)
    if payment_entity is None:
        return response.bad_request()

    try:
        data, evases = infos.prepare(payment_scene, payment_entity)
        return response.success(info=data, activated_evas=evases)
    except Exception as e:
        return response.fail(msg=e.message)


def prepare_params(tx, payment_scene, vas_name):
    from api_x.zyt.user_mapping.auth import vas_payment_is_enabled
    from api_x.zyt.evas.payment import params

    # TODO: log to db.
    logger.info("[PAYMENT PARAMS] {0}, {1}, {2}, {3}".format(payment_scene, vas_name, tx.type, tx.sn))

    # 目前暂时用来控制zyt余额支付仅限于lvye_pay_site.
    if not vas_payment_is_enabled(tx.channel_name, vas_name):
        return response.refused(msg='[{0}] is not allowed for [{1}]'.format(vas_name, tx.channel_name))

    if tx.state != PaymentTxState.CREATED:
        return response.processed()

    payment_entity = gen_payment_entity(tx)
    if payment_entity is None:
        return response.bad_request()

    try:
        payment_type, prepared_params = params.prepare(payment_scene, vas_name, payment_entity)
        return response.success(params=prepared_params, vas_name=vas_name, payment_type=payment_type)
    except Exception as e:
        return response.fail(msg=e.message)


@mod.route("/payment/result", methods=["POST", "GET"])
@verify_request('payment_callback')
def payment_callback():
    """通用支付页面回调"""
    data = request.values
    sn = data['sn']
    result = data['result']
    is_success = result == 'SUCCESS'

    handle = get_pay_notify_handle(TransactionType.PAYMENT, NotifyType.Pay.SYNC)
    if handle:
        # 是否成功，订单号，_数据
        return handle(is_success, sn)

    if is_success:
        return render_template('info.html', title='支付结果', msg='支付成功-订单号:{1}'.format(sn))
    return render_template('info.html', title='支付结果', msg='支付失败-订单号:{1}'.format(sn))
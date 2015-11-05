# coding=utf-8
from __future__ import unicode_literals
from api_x.constant import PaymentTxState

from flask import request, render_template, redirect
from api_x.config import etc as config
from . import web_checkout_entry_mod as mod
from pytoolbox.util.log import get_logger
from api_x.utils.entry_auth import verify_request, checkout_entry
from api_x.constant import RequestClientType
from api_x.utils import req
from .. import gen_payment_entity_by_pay_tx, gen_payment_entity_by_prepaid_tx, get_activated_evases


logger = get_logger(__name__)


def on_not_found():
    # abort(404)
    return render_template("info.html", msg="无此订单")


def on_expired():
    return render_template("info.html", msg="该次支付过期，请重新请求支付")


def on_error():
    return render_template("info.html", msg="请求异常，请重新请求支付")


@mod.route('/<source>/<sn>', methods=['GET'])
def checkout(source, sn):
    """支付收银台入口"""
    # FIXME: Deprecated, just redirect to web checkout.
    return redirect(config.CHECKOUT_URL.format(sn=sn))


@mod.route("/pay/zyt/<sn>", methods=["POST"])
@verify_request('zyt_pay.web')
@checkout_entry(on_not_found=on_not_found, on_expired=on_expired, on_error=on_error)
def zyt_pay(tx, sn):
    """自游通余额支付入口，需要授权"""
    # TODO: 暂时以授权的方式进行，之后需要单独的支付页面/密码
    from api_x.zyt.biz.models import TransactionType
    from api_x.zyt import vas

    request_client_type = req.client_type()
    return do_pay(TransactionType.PAYMENT, tx, vas.NAME, request_client_type)


def do_pay(source, tx, vas_name, request_client_type=RequestClientType.WEB):
    from api_x.zyt.biz.models import TransactionType
    from api_x.zyt.checkout.web_entry import payment

    logger.info("[PAY] {3}, {0}, {1}, {2}".format(source, tx.sn, vas_name, request_client_type))
    if tx.state != PaymentTxState.CREATED:
        return render_template("info.html", msg="该订单已支付")
    if vas_name not in get_activated_evases(tx, with_vas=True):
        # 不支持此支付方式
        return render_template("info.html", msg="不支付此支付方式")

    if source == TransactionType.PAYMENT:
        payment_entity = gen_payment_entity_by_pay_tx(tx)
    elif source == TransactionType.PREPAID:
        payment_entity = gen_payment_entity_by_prepaid_tx(tx)
    else:
        return render_template("info.html", msg="不支持该来源")
    return payment.pay(vas_name, payment_entity, request_client_type)


@mod.route("/pay/result/<source>/<sn>/<vas_name>", methods=["GET"])
def pay_result(source, sn, vas_name):
    data = request.values
    code = data['code']
    vas_sn = data['vas_sn']

    msg = "支付成功" if code == 0 else "支付失败"
    return render_template('pay_result.html', title='支付结果', source=source, sn=sn,
                           vas_name=vas_name, vas_sn=vas_sn, msg=msg)

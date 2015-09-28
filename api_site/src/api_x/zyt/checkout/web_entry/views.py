# coding=utf-8
from __future__ import unicode_literals
from api_x.constant import PaymentTxState
from api_x.zyt.biz.transaction.dba import get_tx_by_sn

from flask import request, render_template, url_for, abort, redirect
from api_x.config import etc as config
from . import web_checkout_entry_mod as mod
from pytoolbox.util.log import get_logger
from api_x.utils.entry_auth import verify_request, limit_referrer
from api_x.constant import RequestClientType
from api_x.utils import req
from .. import gen_payment_entity_by_pay_tx, gen_payment_entity_by_prepaid_tx


logger = get_logger(__name__)


@mod.route('/<source>/<sn>', methods=['GET'])
def checkout(source, sn):
    """支付收银台入口"""
    tx = get_tx_by_sn(sn)
    if tx is None:
        abort(404)
    if tx.state != PaymentTxState.CREATED:
        return render_template("info.html", msg="该订单已支付")

    request_client_type = req.client_type()
    return render_template("checkout.html", root_url=config.HOST_URL, source=source, tx=tx,
                           vases=config.Biz.ACTIVATED_EVAS, request_client_type=request_client_type)


def pay_ex_callback(*arg, **kwargs):
    return render_template("info.html", msg="非法请求")


@mod.route("/pay/<source>/<sn>/<vas_name>", methods=["GET"])
@limit_referrer(config.Biz.VALID_NETLOCS, ex_callback=pay_ex_callback)
def pay(source, sn, vas_name):
    """支付入口, 限制只能从checkout过来"""
    if vas_name not in config.Biz.ACTIVATED_EVAS:
        # 不支持此支付方式
        abort(404)

    request_client_type = req.client_type()
    return do_pay(source, sn, vas_name, request_client_type)


@mod.route("/pay/zyt/<sn>", methods=["POST"])
@verify_request('zyt_pay.web')
def zyt_pay(sn):
    """自游通余额支付入口，需要授权"""
    # TODO: 暂时以授权的方式进行，之后需要单独的支付页面/密码
    from api_x.zyt.biz.models import TransactionType
    from api_x.zyt import vas

    request_client_type = req.client_type()
    return do_pay(TransactionType.PAYMENT, sn, vas.NAME, request_client_type)


def do_pay(source, sn, vas_name, request_client_type=RequestClientType.WEB):
    from api_x.zyt.biz.models import TransactionType
    from api_x.zyt.checkout.web_entry import payment

    logger.info("[PAY] {3}, {0}, {1}, {2}".format(source, sn, vas_name, request_client_type))
    tx = get_tx_by_sn(sn)
    if tx is None:
        return render_template("info.html", msg="无此订单")
    if tx.state != PaymentTxState.CREATED:
        return render_template("info.html", msg="该订单已支付")

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

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

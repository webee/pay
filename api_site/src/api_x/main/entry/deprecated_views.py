# coding=utf-8
from __future__ import unicode_literals

from flask import url_for, redirect
from api_x.config import etc as config
from . import main_entry_mod as mod


@mod.route('/checkout/web/<source>/<sn>', methods=['GET'])
def web_checkout_entry_checkout(source, sn):
    """支付收银台入口"""
    # FIXME: Deprecated, just redirect to web checkout.
    return redirect(config.CHECKOUT_URL.format(sn=sn))


@mod.route("/checkout/app/<source>/<sn>/info", methods=["GET"])
def app_checkout_entry_info(source, sn):
    """app支付info接口
    deprecated之前只有lvye_skiing接入
    """
    from api_x.zyt.evas.payment.config import PaymentScene
    return redirect(config.HOST_URL + url_for('biz_entry.pay_info', sn=sn, payment_scene=PaymentScene.lvye_skiing))


@mod.route("/checkout/app/<source>/<sn>/<vas_name>/params", methods=["GET"])
def app_checkout_entry_params(source, sn, vas_name):
    """app支付params接口
    deprecated之前只有lvye_skiing接入
    """
    from api_x.zyt.evas.payment.config import PaymentScene
    return redirect(config.HOST_URL + url_for('biz_entry.pay_params', sn=sn, payment_scene=PaymentScene.lvye_skiing,
                                              vas_name=vas_name))

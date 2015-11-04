# coding=utf-8
from __future__ import unicode_literals

from flask import render_template, Response, jsonify
from . import checkout_entry_mod as mod
from .constant import VAS_INFOS, VAS_PAYMENT_TYPES
from pub_site.constant import RequestClientType
from pytoolbox.util.log import get_logger
from pub_site.utils.entry_auth import limit_referrer
from pub_site.utils import req
from pub_site import config, pay_client


logger = get_logger(__name__)


@mod.route('/<sn>/result', methods=['GET'])
def pay_result(sn):
    """支付结果
    BAD, EXPIRED, INVALID, ERROR,
    DONE, CREATED
    """
    result = pay_client.get_payment_result(sn)
    if not pay_client.is_success_result(result):
        if result is None:
            res = 'BAD'
        elif result.status_code == 413:
            # 过期
            res = 'EXPIRED'
        elif result.status_code == 404:
            # 找不到
            res = 'INVALID'
        else:
            res = 'ERROR'
        return jsonify(res=res)
    state = result.data['state']
    res = 'CREATED'
    if state != 'CREATED':
        res = 'DONE'
    return jsonify(res=res)


@mod.route('/<sn>', methods=['GET'])
def checkout(sn):
    """支付收银台入口"""
    client_type = req.client_type()

    result = pay_client.get_payment_info(sn, client_type)
    if not pay_client.is_success_result(result):
        return payment_failed(result)
    info = result.data['info']
    if info['state'] != 'CREATED':
        return render_template("checkout/info.html", msg="该订单已支付, 如失败，请重新请求支付")

    vases = result.data['activated_evas']

    # 页面适配
    if client_type == RequestClientType.WEB:
        template = "checkout/checkout.html"
        if len(vases) == 1:
            template = "checkout/one_type_checkout.html"
    else:
        # h5
        template = "checkout/checkout_h5.html"
        if len(vases) == 1:
            template = "checkout/one_type_checkout.html"

    return render_template(template, root_url=config.HOST_URL, sn=sn, info=info,
                           vases=vases, vas_infos=VAS_INFOS, client_type=client_type)


@mod.route("/pay/<sn>/<vas_name>", methods=["GET"])
@limit_referrer(config.Checkout.VALID_NETLOCS)
def pay(sn, vas_name):
    """支付入口, 限制只能从checkout过来"""
    client_type = req.client_type()
    return do_pay(sn, vas_name, client_type)


def do_pay(sn, vas_name, client_type):
    from .constant import WeixinPayType

    payment_type = VAS_PAYMENT_TYPES[vas_name][client_type]
    result = pay_client.get_payment_param(sn, vas_name, payment_type)
    if not pay_client.is_success_result(result):
        return payment_failed(result)

    params = result.data['params']
    if vas_name == 'TEST_PAY':
        url = params['_url']
        return Response(_generate_submit_form(url, params))
    elif vas_name == 'LIANLIAN_PAY':
        url = params['_url']
        return Response(_generate_submit_form(url, params))
    elif vas_name == 'WEIXIN_PAY':
        if payment_type == WeixinPayType.NATIVE:
            code_url = params['code_url']
            info = params['_info']
            callback_url = params['_callback_url']
            return render_template("checkout/wx_pay_native.html", code_url=code_url, info=info, sn=sn,
                                   callback_url=callback_url)
        elif payment_type == WeixinPayType.JSAPI:
            # TODO: 微信内支付
            pass
    return render_template("checkout/info.html", msg="支付方式错误")


def payment_failed(result):
    if result is None:
        msg = "请求支付失败"
    elif result.status_code == 413:
        # 过期
        msg = "本支付链接已过期，请重新发起支付!"
    elif result.status_code == 404:
        msg = "交易号错误或者已失效，请重新发起支付!"
    elif result.status_code == 202:
        msg = "交易已支付，如果失败，请重新发起支付!"
    else:
        msg = "failed: code: {0}, msg: {1}".format(result.data['code'], result.data['msg'])
    return render_template("checkout/info.html", msg=msg)


def _generate_submit_form(url, req_params):
    submit_page = '<meta http-equiv="content-type" content="text/html; charset=UTF-8">'
    submit_page += '<form id="payBillForm" action="{0}" method="POST">'.format(url)
    for key in req_params:
        if key.startswith('_'):
            continue
        submit_page += '''<input type="hidden" name="{0}" value='{1}' />'''.format(key, req_params[key])
    submit_page += '<input type="submit" value="Submit" style="display:none" /></form>'
    submit_page += '<script>document.forms["payBillForm"].submit();</script>'
    return submit_page

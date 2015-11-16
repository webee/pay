# coding=utf-8
from __future__ import unicode_literals

from flask import render_template, Response, jsonify, request, url_for, redirect
from . import checkout_entry_mod as mod
from .constant import VAS_INFOS, REQUEST_CLIENT_PAYMENT_SCENE_MAPPING
from pub_site.checkout.commons import payment_failed, generate_submit_form
from pytoolbox.util.log import get_logger
from pytoolbox.util import urls
from pub_site.utils.entry_auth import pay_limit_referrer
from pub_site.utils import req
from pub_site import config, pay_client
from .utils import get_template


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


@mod.route('/<sn>/callback', methods=['GET'])
def pay_callback(sn):
    """支付结果web回调
    """
    data = pay_client.get_payment_result(sn)
    result = ""
    if pay_client.is_success_result(data):
        state = data.data['state']
        if state != 'CREATED':
            result = 'SUCCESS'

    # pure sn.
    sn = sn.split('$', 1)[0]
    return pay_client.web_payment_callback(sn, result)


@mod.route('/mobile', methods=['GET'])
def checkout_mobile():
    vases = ['TEST_PAY', 'LIANLIAN_PAY', 'WEIXIN_PAY']
    return render_template("checkout/checkout_mobile.html", vases=vases, vas_infos=VAS_INFOS)


@mod.route('/<sn>', methods=['GET'])
def checkout(sn):
    """支付收银台入口"""
    client_type = req.client_type()
    payment_scene = REQUEST_CLIENT_PAYMENT_SCENE_MAPPING[client_type]

    result = pay_client.get_payment_info(sn, payment_scene)
    if not pay_client.is_success_result(result):
        return payment_failed(result)
    info = result.data['info']
    if info['state'] != 'CREATED':
        return render_template(get_template("checkout/info", client_type), msg="该订单已支付, 如失败，请重新请求支付")

    vases = result.data['activated_evas']

    # 页面适配
    if len(vases) == 1:
        template = "checkout/one_type_checkout.html"
    else:
        template = get_template("checkout/checkout", client_type)

    return render_template(template, sn=sn, info=info, vases=vases, vas_infos=VAS_INFOS, client_type=client_type,
                           activated_vas=request.args.get('activated_vas'))


@mod.route("/pay/<sn>/<vas_name>", methods=["GET"])
@pay_limit_referrer(config.Checkout.VALID_NETLOCS)
def pay(sn, vas_name):
    """支付入口, 限制只能从checkout过来"""
    if request.args.get('x') is not None or vas_name.startswith('_') or vas_name[0].isdigit() or sn.isupper():
        # FIXME: 自动判断sn和vas_name
        vas_name, sn = sn, vas_name

    extra_params = {k: v for k, v in request.args.items()} or None
    client_type = req.client_type()
    payment_scene = REQUEST_CLIENT_PAYMENT_SCENE_MAPPING[client_type]
    return do_pay(sn, vas_name, payment_scene, extra_params=extra_params, client_type=client_type)


def do_pay(sn, vas_name, payment_scene, extra_params=None, client_type=None):
    from .constant import WeixinPayType

    result = pay_client.get_payment_param(sn, payment_scene, vas_name, extra_params)
    if not pay_client.is_success_result(result):
        return payment_failed(result, client_type=client_type)

    # echo back vas_name, and payment_type.
    vas_name = result.data['vas_name']
    payment_type = result.data['payment_type']
    params = result.data['params']
    if vas_name == 'TEST_PAY':
        url = params['_url']
        return Response(generate_submit_form(url, params))
    elif vas_name == 'LIANLIAN_PAY':
        url = params['_url']
        return Response(generate_submit_form(url, params))
    elif vas_name == 'WEIXIN_PAY':
        if payment_type == WeixinPayType.NATIVE:
            code_url = params['code_url']
            info = params['_info']
            return render_template("checkout/wx_pay_native.html", code_url=code_url, info=info, sn=sn)
        elif payment_type == WeixinPayType.JSAPI:
            if '_url' in params:
                import urllib
                url = params['_url']
                # FIXME: sn, vas_name exchange
                dest_url = config.HOST_URL + url_for('checkout_entry.pay', sn=vas_name, vas_name=sn, x='')
                redirect_uri = urls.build_url(config.Checkout.WEIXIN_AUTH_REDIRECT_URI, dest_url=dest_url)
                url = url % (urllib.urlencode({'x': redirect_uri})[2:],)
                return redirect(url)
            return render_template("checkout/wx_pay_jsapi.html", params=params, sn=sn)
    elif vas_name == 'ZYT':
        # 自游通余额支付
        url = params['_url']
        params['_sn'] = sn
        return Response(generate_submit_form(url, params, keep_all=True))
    return render_template(get_template("checkout/info", client_type), msg="支付方式错误")

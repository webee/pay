# coding=utf-8
from __future__ import unicode_literals

from api_x.utils import req
from api_x.zyt.evas import test_pay, lianlian_pay, weixin_pay
from api_x.zyt import vas


def prepare(vas_name, payment_type, payment_entity):
    if vas_name == test_pay.NAME:
        return _test_pay_params(payment_type, payment_entity)
    elif vas_name == lianlian_pay.NAME:
        return _lianlian_pay_params(payment_type, payment_entity)
    elif vas_name == weixin_pay.NAME:
        return _weixin_pay_params(payment_type, payment_entity)
    elif vas_name == vas.NAME:
        return _pay_by_zyt_pay(payment_type, payment_entity)

    raise Exception("unknown vas [{0}]".format(vas_name))


def _test_pay_params(payment_type, payment_entity):
    from api_x.zyt.evas.test_pay import payment_param

    return payment_param(payment_type, payment_entity.source, payment_entity.user_id, payment_entity.tx_sn,
                         payment_entity.product_name, payment_entity.amount)


def _lianlian_pay_params(payment_type, payment_entity):
    from api_x.zyt.evas.lianlian_pay import payment_param

    return payment_param(payment_type, payment_entity.source, payment_entity.user_id, payment_entity.user_created_on,
                         req.ip(), payment_entity.tx_sn, payment_entity.tx_created_on, payment_entity.product_name,
                         payment_entity.product_desc, payment_entity.amount)


def _weixin_pay_params(payment_type, payment_entity):
    from api_x.config import weixin_pay
    from api_x.zyt.evas.weixin_pay.payment import payment_param

    # payment_type中包含了wx_name, 使用在app支付的情况
    i = payment_type.find('$')
    if i < 0:
        app_config = weixin_pay.AppConfig()
    else:
        payment_type = payment_type[:i]
        wx_name = payment_type[i+1:]
        app_config = weixin_pay.AppConfig(wx_name)

    params = payment_param(payment_type, payment_entity.source, payment_entity.tx_sn,
                           int(100 * payment_entity.amount), req.ip(), payment_entity.product_name,
                           payment_entity.tx_created_on, detail=payment_entity.product_desc, app_config=app_config)
    if '_info' in params:
        params['_info'] = payment_type.dict()
    return params


def _pay_by_zyt_pay(payment_type, payment_entity):
    from api_x.zyt.vas import payment_param

    return payment_param(payment_type, payment_entity.source, payment_entity.tx_sn)

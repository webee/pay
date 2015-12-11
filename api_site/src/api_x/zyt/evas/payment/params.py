# coding=utf-8
from __future__ import unicode_literals

from api_x.utils import req
from api_x.zyt.evas import test_pay, lianlian_pay, weixin_pay, ali_pay
from api_x.zyt import vas as zyt_pay
from pytoolbox.util.log import get_logger
from . import get_payment_type


logger = get_logger(__name__)


def prepare(payment_scene, vas_name, payment_entity, extra_params=None):
    payment_type = get_payment_type(payment_scene, vas_name)
    logger.info('prepare param: [{0}], [{1}]'.format(vas_name, payment_type))

    if vas_name == test_pay.NAME:
        params = _test_pay_params(payment_type, payment_entity)
    elif vas_name == ali_pay.NAME:
        params = _ali_pay_params(payment_type, payment_entity)
    elif vas_name == weixin_pay.NAME:
        params = _weixin_pay_params(payment_type, payment_entity, extra_params)
    elif vas_name == lianlian_pay.NAME:
        params = _lianlian_pay_params(payment_type, payment_entity)
    elif vas_name == zyt_pay.NAME:
        params = _pay_by_zyt_pay(payment_type, payment_entity)
    else:
        raise Exception("unknown vas [{0}]".format(vas_name))

    return payment_type, params


def _test_pay_params(payment_type, payment_entity):
    from api_x.zyt.evas.test_pay import payment_param

    return payment_param(payment_type, payment_entity.source, payment_entity.user_id, payment_entity.tx_sn,
                         payment_entity.product_name, payment_entity.amount)


def _ali_pay_params(payment_type, payment_entity):
    from api_x.zyt.evas.ali_pay import payment_param

    return payment_param(payment_type, payment_entity.source, payment_entity.tx_sn, payment_entity.product_name,
                         payment_entity.product_desc, payment_entity.amount)


def _lianlian_pay_params(payment_type, payment_entity):
    from api_x.zyt.evas.lianlian_pay import payment_param

    return payment_param(payment_type, payment_entity.source, payment_entity.user_id, payment_entity.user_created_on,
                         req.ip(), payment_entity.tx_sn, payment_entity.tx_created_on, payment_entity.product_name,
                         payment_entity.product_desc, payment_entity.amount)


def _weixin_pay_params(payment_type, payment_entity, extra_params=None):
    from . import config
    from api_x.config import weixin_pay
    from api_x.zyt.evas.weixin_pay.payment import payment_param

    # payment_type中包含了wx_name, 使用在app支付的情况
    payment_type, info = config.get_pure_payment_type_and_info(payment_type)
    if info is None:
        app_config = weixin_pay.AppConfig()
    else:
        wx_name = info
        app_config = weixin_pay.AppConfig(wx_name)

    params = payment_param(payment_type, payment_entity.source, app_config, payment_entity.tx_sn,
                           int(100 * payment_entity.amount), req.ip(), payment_entity.product_name,
                           payment_entity.tx_created_on, detail=payment_entity.product_desc, extra_params=extra_params)
    if '_info' in params:
        params['_info'] = payment_entity.dict()
    return params


def _pay_by_zyt_pay(payment_type, payment_entity):
    from api_x.zyt.vas import payment_param

    return payment_param(payment_type, payment_entity.source, payment_entity.tx_sn)

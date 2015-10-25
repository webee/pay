# coding=utf-8
from __future__ import unicode_literals

from api_x.utils import req
from api_x.zyt.evas import test_pay, lianlian_pay, weixin_pay
from api_x.zyt import vas


def prepare(vas_name, payment_entity):
    if vas_name == test_pay.NAME:
        return _test_pay_params(payment_entity)
    elif vas_name == lianlian_pay.NAME:
        return _lianlian_pay_params(payment_entity)
    elif vas_name == weixin_pay.NAME:
        return _weixin_pay_params(payment_entity)
    elif vas_name == vas.NAME:
        return _pay_by_zyt_pay(payment_entity)

    raise Exception("unknown vas [{0}]".format(vas_name))


def _test_pay_params(payment_entity):
    from api_x.config import test_pay as config
    from api_x.zyt.evas.test_pay import pay

    return pay(payment_entity.source, payment_entity.user_id, payment_entity.tx_sn,
               payment_entity.product_name, payment_entity.amount, channel=config.Pay.Channel.APP)


def _lianlian_pay_params(payment_entity):
    from api_x.config import lianlian_pay as config
    from api_x.zyt.evas.lianlian_pay import pay

    return pay(payment_entity.source, payment_entity.user_id, payment_entity.user_created_on, req.ip(),
               payment_entity.tx_sn, payment_entity.tx_created_on, payment_entity.product_name,
               payment_entity.product_desc, payment_entity.amount, channel=config.Payment.Channel.APP)


def _weixin_pay_params(payment_entity):
    """
    APP支付
    """
    from api_x.config import weixin_pay
    from api_x.zyt.evas.weixin_pay import prepay
    from api_x.zyt.user_mapping import get_channel_by_name

    channel = get_channel_by_name(payment_entity.channel_name)
    app_config = weixin_pay.AppConfig(channel.wx_app)
    return prepay(payment_entity.source, weixin_pay.TradeType.APP, payment_entity.tx_sn,
                  int(100 * payment_entity.amount), req.ip(), payment_entity.product_name, payment_entity.tx_created_on,
                  detail=payment_entity.product_desc,
                  app_config=app_config)


def _pay_by_zyt_pay(payment_entity):
    from api_x.config import etc as config
    from api_x.zyt.vas import pay

    return pay(payment_entity.source, payment_entity.tx_sn, channel=config.Biz.Channel.APP)

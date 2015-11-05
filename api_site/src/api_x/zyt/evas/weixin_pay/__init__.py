# coding=utf-8
from __future__ import unicode_literals

from pytoolbox.util.log import get_logger
from api_x.config import weixin_pay as config
from .commons import generate_absolute_url
from .api_access import request
from .commons import is_success_request, append_md5_sign


NAME = 'WEIXIN_PAY'
VAS_PREFIX = 'WX'
logger = get_logger(__name__)

signers = {}


def is_weixin_pay(vas_name):
    return vas_name.startswith(VAS_PREFIX)


def get_vas_id(app):
    # 此vas_id作为微信支付商户号的唯一id, 记录在各数据库中
    # WEIXIN_PAY为微信支付的总称
    app_config = config.AppConfig(app)
    return '{0}{1}'.format(VAS_PREFIX, app_config.MCH_ID)


def get_app_config_by_vas_id(vas_id):
    # 从vas_id反向得到app_config
    mch_id = vas_id[2:]
    for app_config in config.AppConfig.CONFIGS.values():
        if app_config.MCH_ID == mch_id:
            return app_config


def query_pay_notify(source, out_trade_no, transaction_id='', app_config=None):
    """ 通过主动查询支付订单结果来完成结果通知
    :param source:
    :param out_trade_no:
    :param transaction_id:
    :return:
    """
    from .notify import notify_pay
    from .payment import query_order

    app_config = app_config or config.AppConfig()
    data = query_order(transaction_id, out_trade_no, app_config=app_config)

    return notify_pay(source, app_config.APP_NAME, data)


def query_refund_notify(source):
    from .notify import notify_refund
    from .refund import query_refund

    data = query_refund()

    return notify_refund(source, data)

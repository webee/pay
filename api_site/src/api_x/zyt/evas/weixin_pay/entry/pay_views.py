# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.evas.weixin_pay.commons import is_sending_to_me

from flask import request
from . import weixin_pay_entry_mod as mod
from api_x.zyt.evas.weixin_pay.constant import NotifyType
from api_x.zyt.evas.weixin_pay.notify import get_pay_notify_handle
from api_x.zyt.evas.weixin_pay import get_vas_id
from .commons import parse_and_verify
from . import notify_response
from ..commons import is_success_request
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


@mod.route("/pay/notify/<source>/<app>/", methods=["POST"])
@parse_and_verify
def pay_notify(source, app):
    data = request.verified_data
    appid = data['appid']
    mch_id = data['mch_id']
    out_trade_no = data['out_trade_no']
    transaction_id = data['transaction_id']

    logger.info('pay notify {0}@{1}: {2}'.format(source, app, data))
    if not is_sending_to_me(app, appid, mch_id):
        return notify_response.bad()

    handle = get_pay_notify_handle(source, NotifyType.Pay.ASYNC)
    if handle is None:
        return notify_response.miss()

    try:
        # 此通知的调用协议
        # 是否成功，订单号，来源系统，来源系统订单号，数据
        # TODO: 提出接口
        handle(is_success_request(data), out_trade_no, get_vas_id(app), transaction_id, data)
        return notify_response.succeed()
    except Exception as e:
        logger.exception(e)
        logger.warning('pay notify error: {0}'.format(e.message))
        return notify_response.failed()

# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.evas.lianlian_pay.commons import is_sending_to_me

from flask import request
from . import lianlian_pay_entry_mod as mod
from api_x.zyt.evas.lianlian_pay.notify import get_pay_to_bankcard_notify_handle
from api_x.zyt.evas.test_pay import NAME
from .commons import parse_and_verify
from . import notify_response
from .._pay_to_bankcard import is_success_result, is_failed_result
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


@mod.route("/pay_to_bankcard/notify/<source>", methods=["POST"])
@parse_and_verify
def pay_to_bankcard_notify(source):
    data = request.verified_data
    partner_oid = data['oid_partner']
    order_no = data['no_order']
    paybill_id = data['oid_paybill']
    result = data['result_pay']

    logger.info('pay_to_bankcard notify {0}: {1}'.format(source, data))
    if not is_sending_to_me(partner_oid):
        return notify_response.bad()

    handle = get_pay_to_bankcard_notify_handle(source)
    if handle is None:
        return notify_response.miss()

    if is_success_result(result):
        is_success = True
    elif is_failed_result(result):
        is_success = False
    else:
        return notify_response.retry()

    try:
        # 是否成功，订单号，来源系统，来源系统订单号，数据
        handle(is_success, order_no, NAME, paybill_id, data)
        logger.info('pay_to_bankcard notify success: {0}, {1}'.format(source, order_no))
        return notify_response.succeed()
    except Exception as e:
        logger.exception(e)
        logger.warning('pay_to_bankcard notify error: {0}'.format(e.message))
        return notify_response.failed()

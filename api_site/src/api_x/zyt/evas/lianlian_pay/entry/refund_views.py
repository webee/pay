# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.evas.lianlian_pay.commons import is_sending_to_me

from flask import request
from . import lianlian_pay_entry_mod as mod
from api_x.zyt.evas.lianlian_pay.notify import get_refund_notify_handle
from api_x.zyt.evas.test_pay import NAME
from .commons import parse_and_verify
from . import notification
from ..refund import is_success_status
from tools.mylog import get_logger


logger = get_logger(__name__)


@mod.route("/refund/notify/<source>", methods=["POST"])
@parse_and_verify
def refund_notify(source):
    data = request.verified_data
    partner_oid = data['oid_partner']
    refund_no = data['no_refund']
    status = data['sta_refund']
    refundno_oid = data['oid_refundno']

    logger.info('refund notify {0}: {1}'.format(source, data))
    if not is_sending_to_me(partner_oid):
        return notification.bad()

    handle = get_refund_notify_handle(source)
    if handle is None:
        return notification.miss()

    try:
        # 是否成功，订单号，来源系统，来源系统订单号，数据
        handle(is_success_status(status), refund_no, NAME, refundno_oid, data)
        logger.info('refund notify success: {0}, {1}'.format(source, refund_no))
        return notification.succeed()
    except Exception as e:
        logger.exception(e)
        logger.warning('refund notify error: {0}'.format(e.message))
        return notification.failed()

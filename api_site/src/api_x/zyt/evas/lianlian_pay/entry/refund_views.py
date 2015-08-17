# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.evas.lianlian_pay.commons import is_sending_to_me

from flask import request, render_template
from . import lianlian_pay_entry_mod as mod
from api_x.zyt.evas.lianlian_pay.constant import BizType, NotifyType
from api_x.zyt.evas.lianlian_pay.notify import get_refund_notify_handle
from api_x.zyt.evas.test_pay import NAME
from .commons import parse_and_verify
from . import notification
from api_x.config import lianlian_pay
from tools.mylog import get_logger


logger = get_logger(__name__)


@mod.route("/refund/notify/<refund_source>", methods=["POST"])
@parse_and_verify
def refund_notify(refund_source):
    data = request.verified_data
    partner_oid = data['oid_partner']
    refund_no = data['no_refund']
    status = data['sta_refund']
    refundno_oid = data['oid_refundno']

    logger.info('refund notify {0}: {1}'.format(refund_source, data))
    if not is_sending_to_me(partner_oid):
        return notification.is_invalid()

    handle = get_refund_notify_handle(refund_source)
    if handle:
        try:
            # 是否成功，订单号，来源系统，来源系统订单号，数据
            if handle(is_success_status(status), refund_no, NAME, refundno_oid, data):
                return notification.succeed()
            return notification.is_invalid()
        except Exception as e:
            logger.exception(e)
            return notification.is_invalid()

    return notification.succeed()


def is_success_status(status):
    return status == lianlian_pay.Refund.Status.SUCCESS

# -*- coding: utf-8 -*-
from .api_access import request
from api_x.utils.times import datetime_to_str
from api_x.config import ali_pay
from ..error import ApiError, RefundBalanceInsufficientError
from pytoolbox.util.sign import SignType


def refund(refund_no, refunded_on, amount, paybill_id, notify_url):
    pass


def is_success_or_fail(status):
    return None


def refund_query(refund_no, refunded_on, oid_refundno=''):
    pass

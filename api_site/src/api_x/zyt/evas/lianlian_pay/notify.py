# coding=utf-8
from __future__ import unicode_literals

from .constant import BizType, NotifyType
from api_x.zyt.evas.lianlian_pay.commons import is_sending_to_me
from pytoolbox.util.log import get_logger

logger = get_logger(__name__)


_all_handles = {}


def _register_notify_handle(source, biz_type, notify_type, handle):
    """
    注册通知处理器
    :param source: 来源，比如：支付，充值，退款，提现
    :param biz_type: 连连提供的业务接口类型：支付，退款，代付
    :param notify_type: 同步，异步
    :param handle: 处理函数
    :return:
    """
    source_handles = _all_handles.setdefault(source, {})
    handles = source_handles.setdefault(biz_type, {})
    handles[notify_type] = handle


def _get_notify_handle(source, biz_type, notify_type):
    return _all_handles[source][biz_type][notify_type]


def register_handle(source, biz_type, notify_type):
    def wrap(handle):
        _register_notify_handle(source, biz_type, notify_type, handle)
        return handle
    return wrap


def register_pay_notify_handle(source, notify_type, handle):
    if notify_type not in [NotifyType.Pay.SYNC, NotifyType.Pay.ASYNC]:
        raise ValueError('notify_type: [{0}] not supported.'.format(notify_type))
    _register_notify_handle(source, BizType.PAY, notify_type, handle)


def get_pay_notify_handle(refund_source, notify_type):
    return _get_notify_handle(refund_source, BizType.PAY, notify_type)


def register_refund_notify_handle(source, handle):
    _register_notify_handle(source, BizType.REFUND, NotifyType.Refund.ASYNC, handle)


def get_refund_notify_handle(refund_source):
    return _get_notify_handle(refund_source, BizType.REFUND, NotifyType.Refund.ASYNC)


def register_pay_to_bankcard_notify_handle(source, handle):
    _register_notify_handle(source, BizType.PAY_TO_BANK, NotifyType.Refund.ASYNC, handle)


def get_pay_to_bankcard_notify_handle(source):
    return _get_notify_handle(source, BizType.PAY_TO_BANK, NotifyType.Refund.ASYNC)


# refund
def notify_refund(source, data):
    from . import NAME
    from ._refund import is_success_or_fail
    partner_oid = data['oid_partner']
    refund_no = data['no_refund']
    status = data['sta_refund']
    refundno_oid = data['oid_refundno']

    logger.info('refund notify {0}: {1}'.format(source, data))
    if not is_sending_to_me(partner_oid):
        return NotifyRespTypes.BAD

    handle = get_refund_notify_handle(source)
    if handle is None:
        return NotifyRespTypes.MISS

    result = is_success_or_fail(status)
    if result is None:
        return NotifyRespTypes.RETRY

    try:
        # 是否成功，订单号，来源系统，来源系统订单号，数据
        handle(result, refund_no, NAME, refundno_oid, data)
        logger.info('refund notify success: {0}, {1}'.format(source, refund_no))
        return NotifyRespTypes.SUCCEED
    except Exception as e:
        logger.exception(e)
        logger.warning('refund notify error: {0}'.format(e.message))
        return NotifyRespTypes.FAILED


class NotifyRespTypes:
    SUCCEED = 'SUCCEED'
    FAILED = 'FAILED'
    DUPLICATE = 'DUPLICATE'
    BAD = 'BAD'
    MISS = 'MISS'
    WRONG = 'WRONG'
    RETRY = 'RETRY'

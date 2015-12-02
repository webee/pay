# coding=utf-8
from __future__ import unicode_literals

from api_x.zyt.evas.constant import NotifyRespTypes
from api_x.config import ali_pay
from .constant import BizType, NotifyType
from pytoolbox.util.log import get_logger
from decimal import Decimal
from .commons import is_success_status
from . import NAME

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


# pay
def notify_pay(source, data):
    out_trade_no = data['out_trade_no']
    trade_no = data['trade_no']
    trade_status = data['trade_status']
    total_fee = Decimal(data['total_fee'])
    seller_id = data['seller_id']

    logger.info('query pay notify {0}: {1}'.format(source, data))

    if seller_id != ali_pay.PID:
        return NotifyRespTypes.BAD

    result = is_success_status(trade_status)

    handle = get_pay_notify_handle(source, NotifyType.Pay.ASYNC)
    if handle is None:
        return NotifyRespTypes.MISS

    try:
        if trade_status == ali_pay.TradeStatus.TRADE_SUCCESS:
            # 此通知的调用协议
            # 是否成功，订单号，来源系统，来源系统订单号，数据
            handle(is_success_status(trade_status), out_trade_no, NAME, trade_no, total_fee, data)
        elif trade_status == ali_pay.TradeStatus.TRADE_FINISHED:
            # FIXME: 暂时忽略
            logger.info('pay notify the finish: [{0}]'.format(out_trade_no))
        return NotifyRespTypes.SUCCEED
    except Exception as e:
        logger.exception(e)
        logger.warning('pay notify error: {0}'.format(e.message))
        return NotifyRespTypes.FAILED


# refund
def notify_refund(source, data=None):
    return NotifyRespTypes.RETRY

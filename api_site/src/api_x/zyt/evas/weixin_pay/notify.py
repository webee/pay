# coding=utf-8
from __future__ import unicode_literals
from api_x.zyt.evas.constant import NotifyRespTypes

from .constant import BizType, NotifyType
from api_x.zyt.evas.weixin_pay import get_vas_id
from .commons import is_trade_success_or_fail, is_refund_success_or_fail, is_sending_to_me
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


# pay
def notify_pay(source, app, data):
    appid = data['appid']
    mch_id = data['mch_id']
    out_trade_no = data['out_trade_no']
    transaction_id = data['transaction_id']
    trade_state = data['trade_state']

    logger.info('pay notify {0}@{1}: {2}'.format(source, app, data))
    if not is_sending_to_me(app, appid, mch_id):
        return NotifyRespTypes.BAD

    result = is_trade_success_or_fail(trade_state)
    if result is None:
        return NotifyRespTypes.RETRY

    handle = get_pay_notify_handle(source, NotifyType.Pay.ASYNC)
    if handle is None:
        return NotifyRespTypes.MISS

    try:
        # 是否成功，订单号，来源系统，来源系统订单号，数据
        handle(result, out_trade_no, get_vas_id(app), transaction_id, data)
        return NotifyRespTypes.SUCCEED
    except Exception as e:
        logger.exception(e)
        logger.warning('pay notify error: {0}'.format(e.message))
        return NotifyRespTypes.FAILED


# refund
def notify_refund(source, data, app):
    appid = data['appid']
    mch_id = data['mch_id']
    refund_id = data['refund_id']
    refund_count = int(data['refund_count'])
    idx = refund_count - 1
    out_refund_no = data['out_refund_no_%d' % idx]
    refund_status = data['refund_status_%d' % idx]

    logger.info('refund notify {0}@{1}: {2}'.format(source, app, data))
    if not is_sending_to_me(app, appid, mch_id):
        return NotifyRespTypes.BAD

    result = is_refund_success_or_fail(refund_status)
    if result is None:
        return NotifyRespTypes.RETRY

    handle = get_refund_notify_handle(source)
    if handle is None:
        return NotifyRespTypes.MISS

    try:
        # 是否成功，订单号，来源系统，来源系统订单号，数据
        handle(result, out_refund_no, get_vas_id(app), refund_id, data)
        logger.info('refund notify success: {0}, {1}'.format(source, out_refund_no))
        return NotifyRespTypes.SUCCEED
    except Exception as e:
        logger.exception(e)
        logger.warning('refund notify error: {0}'.format(e.message))
        return NotifyRespTypes.FAILED

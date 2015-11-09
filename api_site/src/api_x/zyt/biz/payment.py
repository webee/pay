# coding=utf-8
import time
from api_x.constant import PaymentTxState, TransactionType
from api_x.zyt.biz.pay import get_payment_tx_by_sn, logger
from api_x.zyt.user_mapping import get_user_map_by_account_user_id


def handle_payment_result(is_success, sn, data=None):
    """
    :param is_success: 是否成功
    :param sn: 订单号
    :param data: 数据
    :return:
    """
    tx = get_payment_tx_by_sn(sn)
    payment_record = tx.record
    client_callback_url = payment_record.client_callback_url

    req_code = 0 if is_success else 1
    code = 0 if tx.state not in [PaymentTxState.FAILED, PaymentTxState.CREATED] else 1
    if tx.state != PaymentTxState.CREATED and client_callback_url:
        # 必须要tx状态改变
        if code != req_code:
            logger.warn('callback result mismatch with notify result.')
            # 等待半秒钟
            time.sleep(0.5)
            code = 0 if tx.state not in [PaymentTxState.FAILED, PaymentTxState.CREATED] else 1
        from api_x.utils.notify import sign_and_return_client_callback
        user_mapping = get_user_map_by_account_user_id(payment_record.payer_id)
        user_id = user_mapping.user_id
        params = {'code': code, 'user_id': user_id, 'sn': payment_record.sn,
                  'order_id': payment_record.order_id, 'amount': payment_record.amount}
        return sign_and_return_client_callback(client_callback_url, tx.channel_name, params, method="POST")

    from flask import jsonify
    return jsonify(code=code, source=TransactionType.PAYMENT, sn=sn)
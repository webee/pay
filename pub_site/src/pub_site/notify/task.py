# coding=utf-8
from __future__ import unicode_literals

from datetime import datetime, timedelta
from pub_site.constant import WithdrawState
from pub_site.withdraw import dba as withdraw_dba
from pub_site import pay_client
from pub_site.sms import sms
from tools.utils import to_bankcard_mask


def fetch_notify_withdraw_result(minutes):
    now = datetime.utcnow()
    d = timedelta(minutes=minutes)
    t = now - d

    withdraw_records = withdraw_dba.get_requested_withdraw_record_before(t)
    for withdraw_record in withdraw_records:
        user_id = withdraw_record.user_id
        sn = withdraw_record.sn
        data = pay_client.query_withdraw(user_id, sn)
        if data is None:
            continue

        is_success = is_withdraw_result_success(data['code'])
        if is_success is not None:
            notify_user_withdraw_result(is_success, withdraw_record)


def is_withdraw_result_success(code):
    if code not in [0, '0', 1, '1']:
        return None

    return code in [0, '0']


def notify_user_withdraw_result(is_success, withdraw_record):
    msg = _build_msg(is_success, withdraw_record)

    notified = sms.send(withdraw_record.phone_no, msg)
    if not notified:
        # 失败再尝试一次，TODO: 使用celery.
        notified = sms.send(withdraw_record.phone_no, msg)

    if notified:
        new_state = WithdrawState.SUCCESS if is_success else WithdrawState.FAILED
        withdraw_dba.update_withdraw_state(withdraw_record.sn, withdraw_record.user_id, new_state)
    return True


def _build_msg(is_success, withdraw_record):
    user_id = withdraw_record.user_id
    bankcard_id = withdraw_record.bankcard_id
    bc = pay_client.app_get_user_bankcard(user_id, bankcard_id)

    params = {
        'created_on': withdraw_record.created_on,
        'amount': withdraw_record.amount,
        'bank_name': bc['bank_name'],
        'card_no': to_bankcard_mask(bc['card_no'])
    }
    if is_success:
        params['actual_amount'] = withdraw_record.actual_amount
        params['fee'] = withdraw_record.fee
        msg = "您于{created_on}提现{amount}到{bank_name}({card_no})的请求已处理，实际金额: {actual_amount}, 手续费: {fee}; 正等待到账，请留意银行卡到账信息。"
    else:
        msg = "您于{created_on}提现{amount}到{bank_name}({card_no})的请求失败。"
    return msg.format(**params)

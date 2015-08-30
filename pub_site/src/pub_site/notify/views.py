# coding=utf-8
from __future__ import unicode_literals
from flask import request, jsonify
from . import notify_mod as mod
from pub_site import pay_client
from pub_site.constant import WithdrawState
from pub_site.sms import sms
from pub_site.withdraw import dba as withdraw_dba
from tools.utils import to_bankcard_mask


@mod.route('/withdraw', methods=['POST'])
@pay_client.verify_request
def notify_withdraw():
    is_verify_pass = request.is_verify_pass
    if not is_verify_pass:
        return jsonify(code=1)

    data = request.params
    code = data['code']
    sn = data['sn']
    user_id = data['user_id']

    withdraw_record = withdraw_dba.get_withdraw_record(sn, user_id)
    if withdraw_record is None:
        return jsonify(code=1)

    if code in [0, '0']:
        # 成功
        withdraw_record = withdraw_dba.update_withdraw_state(withdraw_record.sn, withdraw_record.user_id,
                                                             WithdrawState.SUCCESS)
        msg = _build_msg(True, withdraw_record)
    else:
        # 失败
        withdraw_dba.update_withdraw_state(withdraw_record.sn, withdraw_record.user_id, WithdrawState.FAILED)
        msg = _build_msg(False, withdraw_record)

    if sms.send(withdraw_record.phone_no, msg):
        return jsonify(code=0)
    return jsonify(code=1)


def _build_msg(is_success, withdraw_record):
    user_id = withdraw_record.user_id
    bankcard_id = withdraw_record.bankcard_id
    bc = pay_client.app_get_user_bankcard(user_id, bankcard_id)

    if is_success:
        params = {
            'created_on': withdraw_record.created_on,
            'amount': withdraw_record.amount,
            'bank_name': bc['name'],
            'card_no': to_bankcard_mask(bc['card_no']),
            'actual_amount': withdraw_record.actual_amount,
            'fee': withdraw_record.fee
        }
        msg = "您于{created_on}提现{amount}到{bank_name}({card_no})的请求已处理，实际金额: {actual_amount}, 手续费: {fee}; 正等待到账，请留意银行卡到账信息。"
    else:
        params = {
            'created_on': withdraw_record.created_on,
            'amount': withdraw_record.amount,
            'bank_name': bc['name'],
            'card_no': to_bankcard_mask(bc['card_no'])
        }
        msg = "您于{created_on}提现{amount}到{bank_name}({card_no})的请求失败。"
    return msg.format(**params)

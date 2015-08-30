# coding=utf-8
from __future__ import unicode_literals
from flask import request, jsonify
from . import notify_mod as mod
from pub_site import pay_client
from pub_site.constant import WithdrawState
from pub_site.sms import sms
from pub_site.withdraw import dba as withdraw_dba


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
        withdraw_dba.update_withdraw_state(withdraw_record.sn, withdraw_record.user_id,
                                  WithdrawState.REQUESTED, WithdrawState.SUCCESS)
        msg = "您的提现请求已处理，请等待到账"
    else:
        # 失败
        withdraw_dba.update_withdraw_state(withdraw_record.sn, withdraw_record.user_id,
                                  WithdrawState.REQUESTED, WithdrawState.FAILED)
        msg = "您的提现请求失败"

    if sms.send(withdraw_record.phone_no, msg):
        return jsonify(code=0)
    return jsonify(code=1)

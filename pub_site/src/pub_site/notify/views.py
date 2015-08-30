# coding=utf-8
from __future__ import unicode_literals
from flask import request, jsonify
from . import notify_mod as mod
from pub_site import pay_client
from pub_site.constant import WithdrawState
from pub_site.withdraw import dba as withdraw_dba
from . import task


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

    is_success = task.is_withdraw_result_success(code)
    if is_success is None:
        return jsonify(code=1)

    new_state = WithdrawState.SUCCESS if is_success else WithdrawState.FAILED
    withdraw_record = withdraw_dba.update_withdraw_state(withdraw_record.sn, withdraw_record.user_id, new_state)

    if task.notify_user_withdraw_result(is_success, withdraw_record):
        return jsonify(code=0)
    return jsonify(code=1)

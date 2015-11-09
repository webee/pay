# coding=utf-8
from __future__ import unicode_literals
from flask import request, jsonify, flash, redirect, url_for
from . import notify_mod as mod
from pub_site import pay_client
from pub_site.withdraw import dba as withdraw_dba
from pub_site.pay_to_lvye import dba as pay_to_lvye_dba
from pub_site import constant
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

    if task.notify_user_withdraw_result(is_success, withdraw_record):
        return jsonify(code=0)
    return jsonify(code=1)


@mod.route('/pay_result', methods=['POST'])
@pay_client.verify_request
def pay_result():
    is_verify_pass = request.is_verify_pass
    if not is_verify_pass:
        return "VERIFY ERROR."

    data = request.params
    code = data['code']
    sn = data['sn']
    user_id = data['user_id']
    if code in [0, '0']:
        pay_to_lvye_dba.update_record_state(sn, user_id, constant.PayToLvyeState.SUCCESS)
        flash(u"付款给绿野支付成功！", category="success")
    else:
        pay_to_lvye_dba.update_record_state(sn, user_id, constant.PayToLvyeState.FAILED)
        flash(u"付款给绿野支付失败！", category="error")
    return redirect(url_for("main.index"))

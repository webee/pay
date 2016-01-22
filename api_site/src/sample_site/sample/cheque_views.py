# coding=utf-8
from __future__ import unicode_literals, print_function

from decimal import Decimal
from sample_site import config
from flask import request, render_template, url_for, redirect, jsonify
from . import sample_mod as mod
import simplejson as json
from sample_site import pay_client
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


@mod.route('/draw_cheque', methods=['POST'])
def draw_cheque():
    """写支票"""
    user_id = '96355632'

    params = {
        'amount': Decimal(request.values['amount']),
        'info': Decimal(request.values['amount']),
        'valid_seconds': int(request.values['valid_seconds']),
        'cheque_type': request.values['cheque_type'],
        'notify_url': ''
    }

    result = pay_client.app_draw_cheque(user_id, params=params, ret_result=True)
    return render_template('sample/info.html', title='写支票结果',
                           msg=json.dumps({'status_code': result.status_code, 'data': result.data}))


@mod.route('/cash_cheque', methods=['POST'])
def cash_cheque():
    """兑现支票"""
    user_id = request.values.get('user_id', '').strip() or config.PAYEE

    cash_token = request.values.get('cash_token')

    result = pay_client.app_cash_cheque(user_id, cash_token, ret_result=True)
    return render_template('sample/info.html', title='兑现支票结果',
                           msg=json.dumps({'status_code': result.status_code, 'data': result.data}))


@mod.route('/cash_cheque', methods=['POST'])
def cancel_cheque():
    """取消支票"""
    user_id = '96355632'
    sn = request.values['sn']

    result = pay_client.app_cancel_cheque(user_id, sn, ret_result=True)
    return render_template('sample/info.html', title='取消支票结果',
                           msg=json.dumps({'status_code': result.status_code, 'data': result.data}))


@mod.route('/list_cheque', methods=['GET'])
def list_cheque():
    """list支票"""
    user_id = '96355632'

    result = pay_client.app_list_cheque(user_id)

    return jsonify(cheques=result['cheques'])

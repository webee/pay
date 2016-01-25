# coding=utf-8
from __future__ import unicode_literals
from flask import request, render_template, jsonify
from flask.ext.login import current_user
from . import cheque_mod as mod
from pub_site import pay_client
from pub_site.auth.utils import login_required
from decimal import Decimal
from .. import response


@mod.route('/draw', methods=['POST'])
@login_required
def draw():
    data = request.values
    params = {
        'amount': Decimal(data['amount']),
        'info': data['info'],
        'valid_seconds': 60*60,
        'cheque_type': 'INSTANT'
    }

    user_id = current_user.user_id

    result = pay_client.app_draw_cheque(user_id, params=params)
    if result is not None:
        return response.success(result)
    return response.failed('draw cheque failed.')


@mod.route('/cash', methods=['POST'])
@login_required
def cash():
    pass


@mod.route('/list', methods=['GET'])
@login_required
def list_cheques():
    user_id = current_user.user_id
    result = pay_client.app_list_cheque(user_id)

    return response.success(result['cheques'])

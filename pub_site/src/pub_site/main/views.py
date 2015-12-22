# coding=utf-8
from __future__ import unicode_literals
from flask import request, render_template, jsonify
from flask.ext.login import current_user
from . import main_mod as mod
from pub_site import pay_client
from .transaction import query_transactions
from pub_site.auth.utils import login_required


@mod.route('/main', methods=['GET'])
@login_required
def index():
    uid = current_user.user_id
    balance = pay_client.app_query_user_available_balance(uid)
    return render_template('main/index.html', available_balance='%.2f' % balance)


@mod.route('/transactions', methods=['GET'])
@login_required
def list_transactions():
    from .transaction import TX_VAS_MSG
    uid = current_user.user_id
    data = request.args
    role = data['role']
    page_no = int(data.get('page_no', 1))
    q = data.get('q', '').strip()
    q = q if q else None
    vas_name = data.get('vas_name')

    page_size = 10
    count, transactions = query_transactions(uid, role, page_no, page_size, vas_name, q)
    res = {
        'count': count,
        'page_no': page_no,
        'page_size': page_size,
        'page_count': (count - 1) / page_size + 1,
        'transactions': transactions,
        'vas_name': vas_name
    }
    return render_template('main/tx_list.html', res=res, vases=TX_VAS_MSG)


@mod.route('/available_balance', methods=['GET'])
@login_required
def available_balance():
    uid = current_user.user_id
    balance = pay_client.app_query_user_available_balance(uid)

    return jsonify(available_balance='%.2f' % balance)


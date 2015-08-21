# coding=utf-8
from __future__ import unicode_literals
from flask import request, render_template, jsonify
from flask.ext.login import login_required, current_user
from . import main_mod as mod
from pub_site import pay_client
from .transaction import query_transactions
from ..constant import TradeType


@mod.route('/main', methods=['GET'])
@login_required
def index():
    return render_template('main/index.html')


@mod.route('/transactions', methods=['GET'])
@login_required
def list_transactions():
    uid = current_user.user_id
    data = request.args
    role = data['role']
    page_no = int(data.get('page_no', 1))
    q = data.get('q', '').strip()
    q = q if q else None

    page_size = 10
    count, transactions = query_transactions(uid, role, page_no, page_size, q)
    res = {
        'count': count,
        'page_no': page_no,
        'page_size': page_size,
        'page_count': (count - 1) / page_size + 1,
        'transactions': transactions,
    }
    return render_template('main/tx_list.html', res=res)


@mod.route('/balance', methods=['GET'])
@login_required
def balance():
    uid = current_user.user_id
    balance = pay_client.get_user_available_balance(uid)

    return jsonify(balance=balance)


@mod.route('/trade/<int:id>', methods=['GET'])
@login_required
def trade_detail(id):
    trade = {"id": id, "type": TradeType.WITHDRAW}
    return render_template('main/trade-detail.html', trade=trade)

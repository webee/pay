# coding=utf-8
from __future__ import unicode_literals
from flask import request, render_template, jsonify
from flask.ext.login import login_required, current_user
from . import main_mod as mod
from pub_site import pay_client
from .transaction_log import cash_records, list_trade_orders
from ..constant import TradeType


@mod.route('/', methods=['GET'])
@login_required
def index():
    return render_template('main/index.html')


@mod.route('/transaction_list', methods=['GET'])
@login_required
def transaction_list():
    uid = current_user.user_id
    page_no = int(request.args.get('page_no', 1))
    page_size = int(request.args.get('page_size', 10))
    q = request.args.get('q', '').strip()
    side = request.args.get('side', '')
    tp = request.args.get('tp', '')

    count, records, record_infos = cash_records(uid, q, side, tp, page_no, page_size)

    res = {
        'q': q,
        'count': count,
        'page_no': page_no,
        'page_size': page_size,
        'page_count': (count - 1) / page_size + 1,
        'records': records,
        'record_infos': record_infos,
        }
    return render_template('main/tx_list.html', res=res)


@mod.route('/orders', methods=['GET'])
@login_required
def list_orders():
    uid = current_user.user_id
    data = request.args
    category = data['category']
    page_no = int(data.get('page_no', 1))
    keyword = data.get('keyword', '').strip()
    keyword = None if not keyword else keyword

    page_size = 10
    count, records = list_trade_orders(uid, category, page_no, page_size, keyword)
    res = {
        'count': count,
        'page_no': page_no,
        'page_size': page_size,
        'page_count': (count - 1) / page_size + 1,
        'records': records,
    }
    return render_template('main/tx_list.html', res=res)



@mod.route('/balance', methods=['GET'])
@login_required
def balance():
    uid = current_user.user_id
    balance = pay_client.get_user_balance(uid)

    return jsonify(balance=balance)


@mod.route('/trade/<int:id>', methods=['GET'])
@login_required
def trade_detail(id):
    trade = {"id": id, "type": TradeType.WITHDRAW}
    return render_template('main/trade-detail.html', trade=trade)

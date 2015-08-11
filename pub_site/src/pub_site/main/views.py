# coding=utf-8
from __future__ import unicode_literals
from flask import request, render_template, jsonify
from flask.ext.login import login_required, current_user
from . import main_mod as mod
from pub_site import pay_client
from .transaction_log import cash_records


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
    q = request.args.get('q', '')
    side = request.args.get('side', '')
    tp = request.args.get('tp', '')

    count, records, record_info = cash_records(uid, q, side, tp, page_no, page_size)

    res = {
        'count': count,
        'page_no': page_no,
        'page_size': page_size,
        'page_count': (count - 1) / page_size + 1,
        'records': records,
        'record_infos': record_info,
        }
    return render_template('main/tx_list.html', res=res)


@mod.route('/balance', methods=['GET'])
@login_required
def balance():
    uid = current_user.user_id
    balance = pay_client.get_user_balance(uid)

    return jsonify(balance=balance)

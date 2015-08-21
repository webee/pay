# coding=utf-8
from __future__ import unicode_literals

from flask import request
from api_x.utils import response
from . import biz_entry_mod as mod
from api_x.zyt.biz.transaction import query_user_transactions


@mod.route('/account_users/<int:account_user_id>/transactions', methods=['GET'])
def list_transactions(account_user_id):
    data = request.args
    role = data.get('role')
    page_no = int(data.get('page_no', 1))
    page_size = int(data.get('page_size', 20))
    q = data.get('q')

    total_num, utxs = query_user_transactions(account_user_id, role, page_no, page_size, q)
    txs = [_get_tx(utx) for utx in utxs]

    return response.success(total=total_num, transactions=txs)


def _get_tx(utx):
    tx = utx.tx
    return {
        'role': utx.role,
        'sn': tx.sn,
        'amount': tx.amount,
        'type': tx.type,
        'vas_name': tx.vas_name,
        'state': tx.state,
        'comments': tx.comments,
        'created_on': tx.created_on,
    }

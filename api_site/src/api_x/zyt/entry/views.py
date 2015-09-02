# coding=utf-8
from __future__ import unicode_literals

from flask import request
from api_x.utils import response
from . import biz_entry_mod as mod
from api_x.utils.entry_auth import verify_request
from api_x.zyt.biz.transaction import query_user_transactions


@mod.route('/users/<user_id>/transactions', methods=['GET'])
@verify_request('list_transactions')
def list_transactions(user_id):
    data = request.args
    channel = request.channel
    role = data.get('role')
    page_no = int(data.get('page_no', 1))
    page_size = int(data.get('page_size', 20))
    q = data.get('q')

    user_map = channel.get_user_map(user_id)
    if user_map is None:
        return response.bad_request(msg='user not exists: [{0}]'.format(user_id))
    account_user_id = user_map.account_user_id

    total_num, utxs = query_user_transactions(account_user_id, role, page_no, page_size, q)
    txs = [_get_tx(utx) for utx in utxs]

    return response.success(data={'total': total_num, 'txs': txs})


def _get_tx(utx):
    tx = utx.tx
    return {
        'role': utx.role,
        'sn': tx.sn,
        'order_id': tx.order_id if tx.order_id else '',
        'amount': tx.amount,
        'type': tx.type,
        'vas_name': tx.vas_name,
        'channel_name': tx.channel_name,
        'state': tx.state,
        'comments': tx.comments,
        'created_on': tx.created_on,
    }

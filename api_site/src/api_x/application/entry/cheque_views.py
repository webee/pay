# coding=utf-8
from __future__ import unicode_literals

from api_x.utils import response
from flask import request
from pytoolbox.util.log import get_logger
from api_x.utils.entry_auth import verify_request
from api_x.zyt.biz.models import ChequeType
from . import application_mod as mod
from .. import cheque

logger = get_logger(__name__)


@mod.route('/users/<user_id>/cheque/draw', methods=['POST'])
@verify_request('app_draw_cheque')
def draw_cheque(user_id):
    data = request.values
    channel = request.channel
    order_id = data.get('order_id')
    amount = data['amount']
    valid_seconds = data.get('valid_seconds', 30)
    cheque_type = data.get('cheque_type', ChequeType.INSTANT)
    info = data.get('info', '')
    client_notify_url = data.get('notify_url', '')

    user_map = channel.get_user_map(user_id)
    if user_map is None:
        return response.bad_request(msg='user not exists: [{0}]'.format(user_id))
    from_id = user_map.account_user_id

    try:
        cheque_record = cheque.draw_cheque(channel, from_id, amount, order_id, valid_seconds, cheque_type,
                                           info, client_notify_url)
        return response.success(sn=cheque_record.sn, cash_token=cheque_record.cash_token, amount=cheque_record.amount)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)


@mod.route('/users/<user_id>/cheque/cash', methods=['POST'])
@verify_request('app_cash_cheque')
def cash_cheque(user_id):
    data = request.values
    channel = request.channel
    cash_token = data['cash_token']

    user_map = channel.get_user_map(user_id)
    if user_map is None:
        return response.bad_request(msg='user not exists: [{0}]'.format(user_id))
    to_id = user_map.account_user_id

    try:
        cheque_record = cheque.cash_cheque(channel, to_id, cash_token)
        return response.success(sn=cheque_record.sn, amount=cheque_record.amount)
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)


@mod.route('/users/<user_id>/cheque/cancel', methods=['POST'])
@verify_request('app_cancel_cheque')
def cancel_cheque(user_id):
    data = request.values
    channel = request.channel
    sn = data['sn']

    user_map = channel.get_user_map(user_id)
    if user_map is None:
        return response.bad_request(msg='user not exists: [{0}]'.format(user_id))

    try:
        cheque.cancel_cheque(channel, user_map.account_user_id, sn)
        return response.success()
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)


@mod.route('/users/<user_id>/cheque/list', methods=['GET'])
@verify_request('app_list_cheque')
def list_cheque(user_id):
    data = request.values
    channel = request.channel

    user_map = channel.get_user_map(user_id)
    if user_map is None:
        return response.bad_request(msg='user not exists: [{0}]'.format(user_id))

    try:
        cheque_records = cheque.list_cheque(channel, user_map.account_user_id)
        return response.success(cheques=[{
            'amount': cr.amount,
            'cash_token': cr.cash_token,
            'expired_at': cr.expired_at,
            'created_on': cr.created_on
            } for cr in cheque_records
        ])
    except Exception as e:
        logger.exception(e)
        return response.fail(code=1, msg=e.message)

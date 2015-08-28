# coding=utf-8
from __future__ import unicode_literals

from flask import request
from . import user_mapping_entry_mod as mod
from .. import get_or_create_account_user, get_user_map
from api_x.utils.entry_auth import verify_request
from api_x.utils import response
from api_x.config import etc as config


@mod.route('/users/<user_id>', methods=['GET'])
@verify_request('get_account_user')
def get_account_user(user_id):
    channel = request.channel
    user_domain = channel.user_domain
    user_map = get_user_map(user_domain.id, user_id)
    if user_map is None:
        return response.fail('account user not found'), 404
    return response.success(account_user_id=user_map.account_user_id)


@mod.route('/users/<user_id>', methods=['POST'])
@verify_request('get_create_account_user')
def get_create_account_user(user_id):
    channel = request.channel
    user_domain = channel.user_domain
    account_user_id = get_or_create_account_user(user_domain.id, user_id)
    return response.success(account_user_id=account_user_id)


@mod.route('/users/<user_id>/is_opened', methods=['GET'])
@verify_request('query_user_is_opened')
def query_user_is_opened(user_id):
    channel = request.channel
    user_domain = channel.user_domain

    user_map = get_user_map(user_domain.id, user_id)
    if user_map is None:
        return response.not_found()

    is_opened = config.Biz.IS_ALL_OPENED or user_map.is_opened
    return response.success(is_opened=is_opened)

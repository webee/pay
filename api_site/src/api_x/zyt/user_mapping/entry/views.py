# coding=utf-8
from __future__ import unicode_literals

from . import user_mapping_entry_mod as mod
from .. import get_or_create_account_user, get_user_map
from .. import get_user_domain_by_name
from api_x.utils.entry_auth import verify_request
from api_x.utils import response
from api_x.config import etc as config


@mod.route('/user_domains/<user_domain_name>/users/<user_id>/account_user_id', methods=['GET'])
def get_account_user_id(user_domain_name, user_id):
    user_domain = get_user_domain_by_name(user_domain_name)
    user_map = get_user_map(user_domain.id, user_id)
    if user_map is None:
        return response.fail('account user not found'), 404
    return response.success(account_user_id=user_map.account_user_id)


@mod.route('/user_domains/<user_domain_name>/users/<user_id>', methods=['GET', 'POST'])
def get_create_account_user(user_domain_name, user_id):
    user_domain = get_user_domain_by_name(user_domain_name)
    account_user_id = get_or_create_account_user(user_domain.id, user_id)
    return response.success(account_user_id=account_user_id)


@mod.route('/user_domains/<user_domain_name>/users/<user_id>/is_opened', methods=['GET'])
@verify_request('query_user_is_opened')
def query_user_is_opened(user_domain_name, user_id):
    user_domain = get_user_domain_by_name(user_domain_name)
    if user_domain is None:
        return response.not_found()

    user_map = get_user_map(user_domain.id, user_id)
    if user_map is None:
        return response.not_found()

    is_opened = config.Biz.IS_ALL_OPENED or user_map.is_opened
    return response.success(is_opened=is_opened, opened_on=user_map.opened_on)

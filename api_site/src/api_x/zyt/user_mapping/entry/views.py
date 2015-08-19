# coding=utf-8
from __future__ import unicode_literals

from . import user_mapping_entry_mod as mod
from api_x.util import response
from .. import get_or_create_account_user, get_user_map
from .. import get_user_domain_by_name


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

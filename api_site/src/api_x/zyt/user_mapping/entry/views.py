# coding=utf-8
from __future__ import unicode_literals

from . import user_mapping_entry_mod as mod
from api_x.util import response
from .. import get_or_create_account_user, get_account_user_id_by_by_domain_info


@mod.route('/user_domains/<int:user_domain_id>/users/<user_id>/account_user_id', methods=['GET'])
def get_account_user_id(user_domain_id, user_id):
    account_user_id = get_account_user_id_by_by_domain_info(user_domain_id, user_id)
    if account_user_id is None:
        return response.fail('account user not found'), 404
    return response.success(account_user_id=account_user_id)


@mod.route('/user_domains/<int:user_domain_id>/users/<user_id>', methods=['GET', 'POST'])
def get_create_account_user(user_domain_id, user_id):
    account_user_id = get_or_create_account_user(user_domain_id, user_id)
    return response.success(account_user_id=account_user_id)

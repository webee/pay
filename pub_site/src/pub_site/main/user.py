# coding=utf-8
from __future__ import unicode_literals

from pub_site.pay_client import get_account_info


def format_account_user(account_id):
    account_info = get_account_info(account_id)

    return '{0}[{1}]'.format(account_info['info'], account_info['user_id'])

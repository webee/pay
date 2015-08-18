# coding=utf-8
from __future__ import unicode_literals

from api_x import db
from api_x.dbs import require_transaction_context
from api_x.zyt.user_mapping import create_user_domain, create_channel, find_or_create_account_user_by_channel_info
from api_x.zyt.user_mapping import get_or_create_account_user


def init_data():
    add_vases()
    add_system_users()

    init_test_data()


def add_system_users():
    # user mapping
    # 系统用户
    from api_x.constant import DefaultUserDomain, SECURE_USER_NAME, LVYE_CORP_USER_NAME
    system_user_domain = create_user_domain(DefaultUserDomain.SYSTEM_USER_DOMAIN_NAME)
    lvye_corp_user_domain = create_user_domain(DefaultUserDomain.LVYE_CORP_DOMAIN_NAME)
    lvye_account_user_domain = create_user_domain(DefaultUserDomain.LVYE_ACCOUNT_DOMAIN_NAME)

    # 担保用户(secure)
    _ = get_or_create_account_user(system_user_domain.id, SECURE_USER_NAME)
    # 绿野公司
    _ = get_or_create_account_user(lvye_corp_user_domain.id, LVYE_CORP_USER_NAME)


def add_vases():
    from api_x.zyt.biz.vas import add_vas
    from api_x.zyt import vas as zyt
    from api_x.zyt.evas import test_pay, lianlian_pay

    add_vas(zyt.NAME)
    add_vas(test_pay.NAME)
    add_vas(lianlian_pay.NAME)


def init_test_data():
    from api_x.constant import DefaultUserDomain
    # 测试用户
    # sample渠道#1
    # 测试用户001(test001)
    test_user_domain = create_user_domain(DefaultUserDomain.TEST_DOMAIN_NAME)
    channel = create_channel(test_user_domain.id, 'sample')

    user_id = find_or_create_account_user_by_channel_info(channel.id, 'test001')

# coding=utf-8
from __future__ import unicode_literals, print_function

from api_x.zyt.user_mapping import create_user_domain, create_channel
from api_x.zyt.user_mapping import create_account_user
from api_x.zyt.user_mapping import add_perm_to_channel


def init_data():
    add_vases()
    add_system_users()

    init_test_data()


def add_vases():
    from api_x.zyt.biz.vas import add_vas
    from api_x.zyt import vas as zyt
    from api_x.zyt.evas import test_pay, lianlian_pay

    add_vas(zyt.NAME)
    add_vas(test_pay.NAME)
    add_vas(lianlian_pay.NAME)


def default_create_channel(user_domain_name, channel_name, channel_desc):
    """默认加上查看「是否开通」, 「支付」, 「退款」和「确认支付」权限"""
    channel = create_channel(user_domain_name, channel_name, channel_desc)
    add_perm_to_channel(channel.name, 'query_user_is_opened')
    add_perm_to_channel(channel.name, 'prepay')
    add_perm_to_channel(channel.name, 'refund')
    add_perm_to_channel(channel.name, 'confirm_guarantee_payment')

    return channel


def add_system_users():
    # user mapping
    # 系统用户
    from api_x.constant import DefaultUserDomain, SECURE_USER_NAME, LVYE_CORP_USER_NAME
    from api_x.zyt.user_mapping import set_user_is_opened

    system_user_domain = create_user_domain(DefaultUserDomain.SYSTEM_USER_DOMAIN_NAME, '系统用户')
    lvye_corp_user_domain = create_user_domain(DefaultUserDomain.LVYE_CORP_DOMAIN_NAME, '绿野公司用户')
    lvye_account_user_domain = create_user_domain(DefaultUserDomain.LVYE_ACCOUNT_DOMAIN_NAME, '绿野用户中心')

    # 担保用户(secure)
    _ = create_account_user(system_user_domain.id, SECURE_USER_NAME, '担保用户')
    # 绿野公司
    _ = create_account_user(lvye_corp_user_domain.id, LVYE_CORP_USER_NAME, '绿野公司')

    # 添加渠道: 绿野活动
    default_create_channel(lvye_account_user_domain.name, 'lvye_huodong', '绿野活动')
    default_create_channel(lvye_account_user_domain.name, 'lvye_pay_test', '绿野自游通测试渠道')

    # 添加渠道: 绿野自游通
    channel = default_create_channel(lvye_account_user_domain.name, 'lvye_pay_site', '绿野自游通网站')
    add_perm_to_channel(channel.name, 'get_account_user')
    add_perm_to_channel(channel.name, 'get_create_account_user')
    add_perm_to_channel(channel.name, 'list_transactions')
    add_perm_to_channel(channel.name, 'app_query_bin')
    add_perm_to_channel(channel.name, 'app_bind_bankcard')
    add_perm_to_channel(channel.name, 'app_get_user_bankcard')
    add_perm_to_channel(channel.name, 'app_list_user_bankcards')
    add_perm_to_channel(channel.name, 'app_withdraw')
    add_perm_to_channel(channel.name, 'app_query_user_balance')

    # 添加测试用户iyinbo
    user_id = '169658002'
    account_user_id = create_account_user(lvye_account_user_domain.id, user_id, 'iyinbo测试用户')
    bind_test_bankcard(account_user_id)
    set_user_is_opened(lvye_account_user_domain.name, user_id)


def init_test_data():
    from api_x.constant import DefaultUserDomain
    # 测试用户
    # sample渠道#1
    # 测试用户001(test001)
    test_user_domain = create_user_domain(DefaultUserDomain.TEST_DOMAIN_NAME, '测试用户')
    user_id = create_account_user(test_user_domain.id, 'test001', '测试001')
    bind_test_bankcard(user_id)

    default_create_channel(test_user_domain.name, 'zyt_sample', '自游通sample系统')


def bind_test_bankcard(account_user_id):
    from api_x.application import bankcard

    bankcard_id = bankcard.bind_bankcard(account_user_id, '6217000010057123526', '易旺', False, '110000', '110000', '芍药居支行')

    print('add bankcard: [{0}] to user_id: [{1}]'.format(bankcard_id, account_user_id))

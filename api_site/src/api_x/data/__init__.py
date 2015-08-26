# coding=utf-8
from __future__ import unicode_literals, print_function

from api_x.zyt.user_mapping import create_user_domain, create_channel
from api_x.zyt.user_mapping import create_account_user


def init_data():
    add_vases()
    add_system_users()

    init_test_data()


def init_channel_perms():
    from api_x.zyt.user_mapping import add_perm_to_channel

    add_perm_to_channel('lvye_pay_site', 'query_user_is_opened')


def add_system_users():
    # user mapping
    # 系统用户
    from api_x.constant import DefaultUserDomain, SECURE_USER_NAME, LVYE_CORP_USER_NAME
    system_user_domain = create_user_domain(DefaultUserDomain.SYSTEM_USER_DOMAIN_NAME, '系统用户')
    lvye_corp_user_domain = create_user_domain(DefaultUserDomain.LVYE_CORP_DOMAIN_NAME, '绿野公司用户')
    lvye_account_user_domain = create_user_domain(DefaultUserDomain.LVYE_ACCOUNT_DOMAIN_NAME, '绿野用户中心')

    # 担保用户(secure)
    _ = create_account_user(system_user_domain.id, SECURE_USER_NAME, '担保用户')
    # 绿野公司
    _ = create_account_user(lvye_corp_user_domain.id, LVYE_CORP_USER_NAME, '绿野公司')

    # 添加渠道: 绿野活动
    create_channel(lvye_account_user_domain.id, 'lvye_huodong', '绿野活动')
    create_channel(lvye_account_user_domain.id, 'lvye_pay_test', '绿野自游通测试渠道')

    # 添加渠道: 绿野自游通
    create_channel(lvye_account_user_domain.id, 'lvye_pay_site', '绿野自游通网站')


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
    test_user_domain = create_user_domain(DefaultUserDomain.TEST_DOMAIN_NAME, '测试用户')
    channel = create_channel(test_user_domain.id, 'zyt_sample', '自游通sample系统')

    user_id = create_account_user(channel.user_domain_id, 'test001', '测试001')

    from api_x.application import bankcard

    bankcard_id = bankcard.add_bankcard(user_id, '6217000010057123526', '易旺', False, '110000', '110000', '芍药居支行')

    print('add bankcard: [{0}]'.format(bankcard_id))
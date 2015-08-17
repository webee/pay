# coding=utf-8
from __future__ import unicode_literals

from api_x import db
from api_x.dbs import require_transaction_context
from api_x.zyt.biz.models import Bankcard
from api_x.zyt.user_mapping import create_user_domain, create_channel, find_or_create_account_user_by_channel_info
from api_x.zyt.user_mapping import get_or_create_account_user


def init_data():
    add_vases()
    add_system_users()

    init_test_data()


def add_system_users():
    # user mapping
    # 系统用户
    from api_x.constant import SYSTEM_USER_DOMAIN_NAME, SECURE_USER_NAME
    system_user_domain = create_user_domain(SYSTEM_USER_DOMAIN_NAME)
    # 担保用户(secure)#1
    _ = get_or_create_account_user(system_user_domain.id, SECURE_USER_NAME)


def add_vases():
    from api_x.zyt.biz.vas import add_vas
    from api_x.zyt import vas as zyt
    from api_x.zyt.evas import test_pay

    add_vas(zyt.NAME)
    add_vas(test_pay.NAME)


def init_test_data():
    # 测试用户
    # sample渠道#1
    # 测试用户001(test001)#2
    user_domain = create_user_domain('测试用户')
    channel = create_channel(user_domain.id, 'sample')

    user_id = find_or_create_account_user_by_channel_info(channel.id, 'test001')

    # test001绑定银行卡#1
    with require_transaction_context():
        bankcard = Bankcard(user_id=user_id, card_no='123', card_type='DEBIT', account_name='test',
                            flag='0', bank_code='123', province_code='123', city_code='123',
                            bank_name='中国建设银行', branch_bank_name='xx支行')

        db.session.add(bankcard)

# coding=utf-8
from pytoolbox.util.pmc_config import read_string


HOST_URL = "http://localhost:8089"


class App:
    import os

    SECRET_KEY = os.environ.get('SECRET_KEY') or '.yek eyvl'
    TESTING = False
    DEBUG = True

PAYEE = 'test001'


class PayClientConfig:
    MD5_KEY = read_string('conf/sample_site/md5_key.txt')
    LVYE_PUB_KEY = read_string('conf/sample_site/lvye_pub_key.txt')
    CHANNEL_PRI_KEY = read_string('conf/sample_site/channel_pri_key.txt')

    # 测试用户
    USER_DOMAIN_NAME = 'testing'
    # sample
    CHANNEL_NAME = 'zyt_sample'

    ROOT_URL = "http://pay.lvye.com/api"
    PREPAID_URL = '/biz/prepaid'
    PREPAY_URL = '/biz/prepay'
    CONFIRM_GUARANTEE_PAYMENT_URL = '/biz/pay/guarantee_payment/confirm'
    REFUND_URL = '/biz/refund'
    WITHDRAW_URL = '/application/account_users/{account_user_id}/withdraw'

    GET_CREATE_ACCOUNT_ID_URL = '/user_mapping/user_domains/{user_domain_name}/users/{user_id}'
    GET_USER_BALANCE_URL = "/vas/zyt/account_users/{account_user_id}/balance"
    LIST_USER_BANKCARDS_URL = 'application/account_users/{account_user_id}/bankcards'

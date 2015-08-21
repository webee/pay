# coding=utf-8


HOST_URL = "http://localhost:8089"


class App:
    import os

    SECRET_KEY = os.environ.get('SECRET_KEY') or '.yek eyvl'
    TESTING = False
    DEBUG = True

PAYEE = 'test001'


class PayAPI:
    # 测试用户
    USER_DOMAIN_NAME = 'testing'
    # sample
    CHANNEL_NAME = 'zyt_sample'

    ROOT_URL = "http://pay.lvye.com/api"
    PREPAID_URL = '/biz/prepaid'
    PRE_PAY_URL = '/biz/pre_pay'
    CONFIRM_GUARANTEE_PAYMENT_URL = '/biz/pay/guarantee_payment/confirm'
    REFUND_URL = '/biz/refund'
    WITHDRAW_URL = '/application/account_users/{account_user_id}/withdraw'

    GET_CREATE_ACCOUNT_ID_URL = '/user_mapping/user_domains/{user_domain_name}/users/{user_id}'
    GET_USER_BALANCE_URL = "/vas/zyt/account_users/{account_user_id}/balance"

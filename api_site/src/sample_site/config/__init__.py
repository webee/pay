# coding=utf-8


HOST_URL = "http://localhost:8089"


class App:
    import os

    SECRET_KEY = os.environ.get('SECRET_KEY') or '.yek eyvl'
    TESTING = False
    DEBUG = True


class PayAPI:
    # 测试用户
    USER_DOMAIN_ID = 2
    # sample
    CHANNEL_ID = 1

    ROOT_URL = "http://pay.lvye.vom/api"
    PREPAID_URL = '/prepaid'
    PRE_PAY_URL = '/pre_pay'
    CONFIRM_GUARANTEE_PAYMENT_URL = '/pay/guarantee_payment/confirm'
    REFUND_URL = '/refund'

    GET_CREATE_ACCOUNT_ID_URL = '/user_mapping/user_domains/{user_domain_id}/users/{user_id}'
    GET_USER_BALANCE_URL = "/vas/zyt/account_users/{account_user_id}/balance"


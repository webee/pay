# coding=utf-8


class Config:
    MD5_KEY = ''
    LVYE_PUB_KEY = ''
    CHANNEL_PRI_KEY = ''
    # 测试用户
    USER_DOMAIN_NAME = 'testing'
    # sample
    CHANNEL_NAME = 'zyt_sample'

    ROOT_URL = "http://pay.lvye.com/api/__"
    PREPAID_URL = '/biz/prepaid'
    PREPAY_URL = '/biz/prepay'
    CONFIRM_GUARANTEE_PAYMENT_URL = '/biz/pay/guarantee_payment/confirm'
    REFUND_URL = '/biz/refund'
    WITHDRAW_URL = '/application/account_users/{account_user_id}/withdraw'

    GET_CREATE_ACCOUNT_ID_URL = '/user_mapping/user_domains/{user_domain_name}/users/{user_id}'
    GET_USER_BALANCE_URL = "/vas/zyt/account_users/{account_user_id}/balance"
    LIST_USER_BANKCARDS_URL = 'application/account_users/{account_user_id}/bankcards'

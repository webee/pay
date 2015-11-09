# coding=utf-8
from __future__ import unicode_literals
from pub_site.constant import RequestClientType

VAS_INFOS = {
    'TEST_PAY': {
        'name': '测试付',
        'desc': '随意付'
    },
    'LIANLIAN_PAY': {
        'name': '银行卡',
        'desc': '快捷支付，无需开通网银'
    },
    'ALI_PAY': {
        'name': '支付宝',
        'desc': '登录支付宝账户或手机支付宝扫码支付'
    },
    'WEIXIN_PAY': {
        'name': '微信',
        'desc': '微信扫码支付'
    },
}


class WeixinPayType:
    NATIVE = 'NATIVE'
    JSAPI = 'JSAPI'


# request client与支付场景的映射
REQUEST_CLIENT_PAYMENT_SCENE_MAPPING = {
    RequestClientType.WEB: 'WEB',
    RequestClientType.WAP: 'WAP',
    RequestClientType.WEIXIN: 'WEIXIN',
}

# coding=utf-8
from __future__ import unicode_literals
from pub_site.constant import RequestClientType

class WeixinPayType:
    NATIVE = 'NATIVE'
    JSAPI = 'JSAPI'


# request client与支付场景的映射
REQUEST_CLIENT_PAYMENT_SCENE_MAPPING = {
    RequestClientType.WEB: 'WEB',
    RequestClientType.WAP: 'WAP',
    RequestClientType.WEIXIN: 'WEIXIN',
}

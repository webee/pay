# coding=utf-8
from __future__ import unicode_literals
from collections import OrderedDict
from api_x.config import zyt_pay, test_pay, lianlian_pay, weixin_pay
from api_x.zyt.vas import NAME as ZYT_PAY
from api_x.zyt.evas.test_pay import NAME as TEST_PAY
from api_x.zyt.evas.lianlian_pay import NAME as LIANLIAN_PAY
from api_x.zyt.evas.weixin_pay import NAME as WEIXIN_PAY
from api_x.zyt.evas.ali_pay import NAME as ALI_PAY


class PaymentScene:
    WEB = 'WEB'  # 一般电脑端网页
    WAP = 'WAP'  # 手机端网页
    WEIXIN = 'WEIXIN'  # 微信内网页
    lvye_skiing = 'lvye_skiing'  # 绿野滑雪app
    # lvye_skiing_wp = 'lvye_skiing_wp' # 绿野滑雪windows phone app

PAYMENT_TYPE_WEIGHTS = {
    TEST_PAY: 0,
    WEIXIN_PAY: 1,
    LIANLIAN_PAY: 2,
    ZYT_PAY: 3,
}

# 所有支持的支付场景
PAYMENT_SCENES = {
    PaymentScene.WEB,
    PaymentScene.WAP,
    PaymentScene.WEIXIN,
    PaymentScene.lvye_skiing,
}


# 各支付场景与第三方支付的支付方式的关联
PAYMENT_SCENE_VASE_TYPES = {
    PaymentScene.WEB: OrderedDict([
        (ZYT_PAY, zyt_pay.PaymentType.WEB),
        (TEST_PAY, test_pay.PaymentType.WEB),
        (LIANLIAN_PAY, lianlian_pay.PaymentType.WEB),
        (WEIXIN_PAY, weixin_pay.PaymentType.NATIVE),
    ]),
    PaymentScene.WAP: OrderedDict([
        #(ZYT_PAY, zyt_pay.PaymentType.WEB),
        (TEST_PAY, test_pay.PaymentType.WEB),
        (LIANLIAN_PAY, lianlian_pay.PaymentType.WAP),
        (WEIXIN_PAY, weixin_pay.PaymentType.JSAPI),
    ]),
    PaymentScene.WEIXIN: OrderedDict([
        #(ZYT_PAY, zyt_pay.PaymentType.WEB),
        (TEST_PAY, test_pay.PaymentType.WEB),
        (LIANLIAN_PAY, lianlian_pay.PaymentType.WAP),
        (WEIXIN_PAY, weixin_pay.PaymentType.JSAPI),
    ]),
    PaymentScene.lvye_skiing: OrderedDict([
        #(ZYT_PAY, zyt_pay.PaymentType.APP),
        (TEST_PAY, test_pay.PaymentType.APP),
        (LIANLIAN_PAY, lianlian_pay.PaymentType.APP),
        (WEIXIN_PAY, weixin_pay.PaymentType.APP + '$lvye_skiing'),
    ]),
}

VAS_INFOS = {
    ZYT_PAY: {
        'name': '自游通',
        'desc': '余额支付'
    },
    TEST_PAY: {
        'name': '测试付',
        'desc': '随意付'
    },
    LIANLIAN_PAY: {
        'name': '银行卡',
        'desc': '借记卡/信用卡 快捷支付'
    },
    ALI_PAY: {
        'name': '支付宝',
        'desc': '支付宝账户、支付宝网银及手机支付宝扫码支付'
    },
    WEIXIN_PAY: {
        'name': '微信',
        'desc': '微信内支付或扫码支付'
    },
}

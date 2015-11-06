# coding=utf-8
from __future__ import unicode_literals
from collections import OrderedDict
from api_x.config import test_pay, lianlian_pay, weixin_pay
from api_x.zyt.evas.test_pay import NAME as TEST_PAY
from api_x.zyt.evas.lianlian_pay import NAME as LIANLIAN_PAY
from api_x.zyt.evas.weixin_pay import NAME as WEIXIN_PAY


class PaymentScene:
    WEB = 'WEB'  # 一般电脑端网页
    WAP = 'WAP'  # 手机端网页
    WEIXIN = 'WEIXIN'  # 微信内网页
    lvye_skiing = 'lvye_skiing'  # 绿野滑雪app
    # lvye_skiing_wp = 'lvye_skiing_wp' # 绿野滑雪windows phone app


# 所有支持的支付场景
PAYMENT_SCENES = {
    PaymentScene.WEB,
    PaymentScene.WAP,
    PaymentScene.WEIXIN,
    PaymentScene.lvye_skiing,
}


# 各支付场景与第三方支付的支付方式的关联
PAYMENT_SCENE_VASE_TYPES = {
    PaymentScene.WEB: OrderedDict({
        TEST_PAY: test_pay.PaymentType.WEB,
        LIANLIAN_PAY: lianlian_pay.PaymentType.WEB,
        WEIXIN_PAY: weixin_pay.PaymentType.NATIVE,
    }),
    PaymentScene.WAP: OrderedDict({
        TEST_PAY: test_pay.PaymentType.WEB,
        LIANLIAN_PAY: lianlian_pay.PaymentType.WAP,
        #WEIXIN_PAY: weixin_pay.PaymentType.JSAPI,
    }),
    PaymentScene.WEIXIN: OrderedDict({
        TEST_PAY: test_pay.PaymentType.WEB,
        LIANLIAN_PAY: lianlian_pay.PaymentType.WAP,
        #WEIXIN_PAY: weixin_pay.PaymentType.JSAPI,
    }),
    PaymentScene.lvye_skiing: OrderedDict({
        TEST_PAY: test_pay.PaymentType.APP,
        LIANLIAN_PAY: lianlian_pay.PaymentType.APP,
        WEIXIN_PAY: weixin_pay.PaymentType.APP + '$lvye_skiing',
    }),
}

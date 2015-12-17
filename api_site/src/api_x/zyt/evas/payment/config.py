# coding=utf-8
from __future__ import unicode_literals
from collections import OrderedDict
from api_x.config import zyt_pay, test_pay, lianlian_pay, weixin_pay, ali_pay
from api_x.zyt.vas import NAME as ZYT_PAY
from api_x.zyt.evas.test_pay import NAME as TEST_PAY
from api_x.zyt.evas.lianlian_pay import NAME as LIANLIAN_PAY
from api_x.zyt.evas.weixin_pay import NAME as WEIXIN_PAY
from api_x.zyt.evas.ali_pay import NAME as ALI_PAY


class PaymentScene:
    WEB = 'WEB'  # 一般电脑端网页
    WAP = 'WAP'  # 手机端网页
    WEIXIN = 'WEIXIN'  # 微信内网页
    APP = 'APP'  # app
    lvye_skiing = 'lvye_skiing'  # 绿野滑雪app
    # lvye_skiing_wp = 'lvye_skiing_wp' # 绿野滑雪windows phone app
    lvye_pay_sdk_demo = 'lvye_pay_sdk_demo'  # 绿野支付demo app

PAYMENT_TYPE_WEIGHTS = {
    TEST_PAY: 0,
    ALI_PAY: 1,
    WEIXIN_PAY: 2,
    LIANLIAN_PAY: 3,
    ZYT_PAY: 4,
}

# 所有支持的支付场景
PAYMENT_SCENES = {
    PaymentScene.WEB,
    PaymentScene.WAP,
    PaymentScene.WEIXIN,
    PaymentScene.lvye_skiing,
    # other apps.
}

# conditions
def gen_cond_is_env(p):
    def is_env(**kwargs):
        from api_x.config import etc as config
        return config.__env_name__ == p
    return is_env


def gen_cond_satisfy_version():
    def satisfy_version(version, **kwargs):
        from api_x.config import etc as config
        print(version)
        print(kwargs)
        return version >= config.VERSION
    return satisfy_version


def is_condition_pass(t, **kwargs):
    # conditional vas.
    if isinstance(t, dict):
        conds = t.get('conditions')
        return all(cond(**kwargs) for cond in conds)
    return True


def get_pure_payment_scene(payment_scene):
    """ <payment_scene>.<vas_name>$<info>.<vas_name>$<info>
    """
    return payment_scene.split('.', 1)[0]


def get_real_payment_type(payment_type, **kwargs):
    if not is_condition_pass(payment_type, **kwargs):
        return None
    if isinstance(payment_type, dict):
        payment_type = payment_type.get('value')
    return payment_type


def get_pure_payment_type_and_info(payment_type):
    """ <payment_type>$<info>
    """
    res = payment_type.split('$', 1)
    if len(res) == 2:
        return res
    return res[0], None


def get_complex_payment_type(vas_name, payment_type, payment_scene):
    """ <payment_scene>.<vas_name>$<info>.<vas_name>$<info>
    :param vas_name:
    :param payment_type:
    :param payment_scene:
    :return:
    """
    extra_type_infos = dict(x.split('$', 1) for x in payment_scene.split('.', 1)[1:])
    if vas_name in extra_type_infos:
        return payment_type + '$' + extra_type_infos[vas_name]
    return payment_type


# 各支付场景与第三方支付的支付方式的关联
PAYMENT_SCENE_VASE_TYPES = {
    PaymentScene.WEB: {
        ZYT_PAY: zyt_pay.PaymentType.WEB,
        TEST_PAY: test_pay.PaymentType.WEB,
        LIANLIAN_PAY: lianlian_pay.PaymentType.WEB,
        WEIXIN_PAY: weixin_pay.PaymentType.NATIVE,
        ALI_PAY: ali_pay.PaymentType.WEB,
    },
    PaymentScene.WAP: {
        #ZYT_PAY: zyt_pay.PaymentType.WEB,
        TEST_PAY: test_pay.PaymentType.WEB,
        LIANLIAN_PAY: lianlian_pay.PaymentType.WAP,
        WEIXIN_PAY: weixin_pay.PaymentType.JSAPI,
        ALI_PAY: ali_pay.PaymentType.WAP,
    },
    PaymentScene.WEIXIN: {
        #ZYT_PAY: zyt_pay.PaymentType.WEB,
        TEST_PAY: test_pay.PaymentType.WEB,
        LIANLIAN_PAY: lianlian_pay.PaymentType.WAP,
        WEIXIN_PAY: weixin_pay.PaymentType.JSAPI,
        ALI_PAY: ali_pay.PaymentType.WAP,
    },
    PaymentScene.APP: {
        TEST_PAY: test_pay.PaymentType.APP,
        LIANLIAN_PAY: lianlian_pay.PaymentType.APP,
        ALI_PAY: ali_pay.PaymentType.APP,
    },
    PaymentScene.lvye_pay_sdk_demo: {
        TEST_PAY: test_pay.PaymentType.APP,
        LIANLIAN_PAY: lianlian_pay.PaymentType.APP,
        ALI_PAY: ali_pay.PaymentType.APP,
        WEIXIN_PAY: weixin_pay.PaymentType.APP,
    },
    PaymentScene.lvye_skiing: {
        TEST_PAY: test_pay.PaymentType.APP,
        LIANLIAN_PAY: lianlian_pay.PaymentType.APP,
        ALI_PAY: {
            'value': ali_pay.PaymentType.APP,
            'conditions': [gen_cond_satisfy_version()]
        },
        WEIXIN_PAY: weixin_pay.PaymentType.APP + '$lvye_skiing',
    },
}


VAS_INFOS = {
    ZYT_PAY: {
        'name': '绿野自游通',
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
        'desc': '推荐有支付宝账号的用户使用'
    },
    WEIXIN_PAY: {
        'name': '微信支付',
        'desc': '微信内支付或扫码支付'
    },
}

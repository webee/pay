# coding=utf-8


def init():
    """各适配系统的初始化"""
    _lianlian_pay_init()
    _weixin_pay_init()
    _ali_pay_init()


def _ali_pay_init():
    from ali_pay import signer
    from api_x.config import ali_pay

    signer.init(ali_pay.MD5_KEY, ali_pay.LVYE_PRI_KEY, ali_pay.ALI_PUB_KEY)


def _lianlian_pay_init():
    from lianlian_pay import signer
    from api_x.config import lianlian_pay

    signer.init(lianlian_pay.MD5_KEY, lianlian_pay.LVYE_PRI_KEY, lianlian_pay.YT_PUB_KEY)


def _weixin_pay_init():
    from pytoolbox.util.sign import Signer
    from weixin_pay import signers
    from api_x.config import weixin_pay

    for name in weixin_pay.AppConfig.CONFIGS.keys():
        app_config = weixin_pay.AppConfig(name)
        signer = Signer('key', 'sign', ignore_case=False, use_uppercase=True, md5_key=app_config.API_KEY)
        signers[name] = signer

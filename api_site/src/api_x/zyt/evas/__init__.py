# coding=utf-8


def init():
    """各适配系统的初始化"""
    from lianlian_pay import signer
    from api_x.config import lianlian_pay

    signer.init(lianlian_pay.MD5_KEY, lianlian_pay.LVYE_PRI_KEY, lianlian_pay.YT_PUB_KEY)

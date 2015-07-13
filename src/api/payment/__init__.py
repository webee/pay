# -*- coding: utf-8 -*-
from flask import Blueprint
from api. attr_dict import AttrDict
from api.base_config import lianlian_base_config

pay_mod = Blueprint('payment', __name__)

lianlian_payment_config = AttrDict(
    busi_partner=AttrDict(
        virtual_goods='101001',
        physical_goods='109001',
    ),

    default_order_expiration='10080',

    payment=AttrDict(
        url='https://yintong.com.cn/payment/bankgateway.htm',
        notify_url='www.baidu.com/notify',
        return_url='www.baidu.com/return'
    )
)
config = lianlian_payment_config.merge_to(lianlian_base_config)

from . import views

# -*- coding: utf-8 -*-
from api.attr_dict import AttrDict
from api.base_config import lianlian_base_config
from flask import Blueprint

refund_mod = Blueprint('refund', __name__)

lianlian_refund_config = AttrDict(
    refund=AttrDict(
        url='https://yintong.com.cn/traderapi/refund.htm',
        notify_url='/refund/{uuid}/result',
    )
)
config = lianlian_refund_config.merge_to(lianlian_base_config)

from . import views

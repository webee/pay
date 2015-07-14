# -*- coding: utf-8 -*-
from api.attr_dict import AttrDict
from flask import Blueprint

refund_mod = Blueprint('refund', __name__)

lianlian_refund_config = AttrDict(
    payment=AttrDict(
        url='https://yintong.com.cn/traderapi/refund.htm',
        notify_url='',
    )
)

from . import views

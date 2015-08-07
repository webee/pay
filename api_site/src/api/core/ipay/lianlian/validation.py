# -*- coding: utf-8 -*-
from api import config


def is_sending_to_me(partner_id):
    return partner_id == config.LianLianPay.OID_PARTNER
# -*- coding: utf-8 -*-
from . import config


def is_sending_to_me(partner_id):
    return partner_id == config.oid_partner
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from . import card_mod as mod
from flask import jsonify
from api import lianlian_service as service

log = logging.getLogger(__name__)


@mod.route('/<card_no>/bin', methods=['GET'])
def query_bin(card_no):
    data = service.bankcard_query(card_no)

    if data['ret']:
        return jsonify(ret=True,
                       bank_code=data['bank_code'],
                       bank_name=data['bank_name'],
                       card_type=data['card_type'])
    return jsonify(ret=False, msg="查询失败")

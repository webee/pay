# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from flask import jsonify
from . import card_mod as mod
from .bankcard_bin import query_bankcard_bin
from old_api.util import response

log = logging.getLogger(__name__)


@mod.route('/<card_no>/bin', methods=['GET'])
def query_bin(card_no):
    card = query_bankcard_bin(card_no)
    if card:
        return jsonify(card)
    return response.not_found()


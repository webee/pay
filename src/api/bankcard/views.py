# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from . import card_mod as mod
from flask import jsonify

log = logging.getLogger(__name__)


@mod.route('/<card_no>/bin', methods=['POST'])
def query_bin(card_no):
    return jsonify({})

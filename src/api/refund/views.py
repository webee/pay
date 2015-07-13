# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from . import refund_mod as mod
from flask import jsonify

log = logging.getLogger(__name__)


@mod.route('/refund', methods=['POST'])
def refund():
    return jsonify({})

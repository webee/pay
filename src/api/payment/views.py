# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from . import pay_mod as mod
from flask import jsonify

log = logging.getLogger(__name__)


@mod.route('/pre-pay', methods=['POST'])
def prepay():
    return jsonify({})


@mod.route('/pay/<id>', methods=['GET'])
def pay(id):
    return jsonify({})


@mod.route('/pay-result', methods=['POST'])
def notify_payment():
    return jsonify({})

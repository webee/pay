# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from . import account_mod as mod
from flask import jsonify

log = logging.getLogger(__name__)


@mod.route('/<account_id>/withdraw', methods=['POST'])
def withdraw(account_id):
    return jsonify({})

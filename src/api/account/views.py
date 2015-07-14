# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import json
import logging

import bankcard
from . import account_mod as mod
from flask import jsonify

log = logging.getLogger(__name__)


@mod.route('/<int:account_id>/withdraw', methods=['POST'])
def withdraw(account_id):
    return jsonify({})


@mod.route('/<int:account_id>/bankcards', methods=['GET'])
def list_all(account_id):
    bankcards = bankcard.list_all(account_id)
    return json.dumps(bankcards), 200

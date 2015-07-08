# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from flask import jsonify
from . import account_mod as mod


log = logging.getLogger(__name__)


@mod.route('/<int:account_id>/bankcards')
def list_bankcards(account_id):
    return jsonify({})

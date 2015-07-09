# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import json
import logging

from . import account_mod as mod
from services import bankcard

log = logging.getLogger(__name__)

@mod.route('/<int:account_id>/bankcards')
def list_bankcards(account_id):
    bankcards = bankcard.list_all(account_id)
    return json.dumps(bankcards), 200


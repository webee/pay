# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from . import account_mod as mod
from tools.mylog import get_logger

logger = get_logger(__name__)


@mod.route('/<int:account_id>/trading_records', methods=['POST'])
def trading_records(account_id):
    pass

# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from . import account_mod as mod
from tools.mylog import get_logger
from .trading import dba
from api.util import response

logger = get_logger(__name__)


@mod.route('/<int:account_id>/cash_events', methods=['GET'])
def trading_records(account_id):
    cash_events = dba.get_cash_events(account_id)

    return response.list_data(cash_events)

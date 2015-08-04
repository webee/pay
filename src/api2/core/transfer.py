# -*- coding: utf-8 -*-
from .bookkeeping import bookkeep, Event, SourceType
from .dba import new_transfer
from pytoolbox.util.dbe import transactional


@transactional
def transfer(trade_id, payer_account_id, payee_account_id, amount):
    new_transfer(trade_id, payer_account_id, payee_account_id, amount)
    bookkeep(Event(SourceType.TRANSFER, trade_id, amount),
             (payer_account_id, '-cash'),
             (payee_account_id, '+cash'))

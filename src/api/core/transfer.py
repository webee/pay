# -*- coding: utf-8 -*-
from ._bookkeeping import bookkeep, Event, SourceType
from ._dba import create_transfer
from pytoolbox.util.dbe import transactional


@transactional
def transfer(trade_id, payer_account_id, payee_account_id, amount):
    create_transfer(trade_id, payer_account_id, payee_account_id, amount)
    bookkeep(Event(SourceType.TRANSFER, trade_id, amount),
             (payer_account_id, '-cash'),
             (payee_account_id, '+cash'))

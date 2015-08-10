# -*- coding: utf-8 -*-
from ._bookkeeping import Event, SourceType, bookkeep
from ._dba import create_transfer
from .balance import get_cash_balance, InsufficientBalanceError
from pytoolbox.util.dbe import transactional


@transactional
def transfer(trade_id, trade_info, payer_account_id, payee_account_id, amount):
    payer_account_balance = get_cash_balance(payer_account_id)
    if payer_account_balance < amount:
        raise InsufficientBalanceError()

    transfer_id = create_transfer(trade_id, trade_info, payer_account_id, payee_account_id, amount)
    bookkeep(Event(SourceType.TRANSFER, transfer_id, amount, trade_info),
             (payer_account_id, '-cash'),
             (payee_account_id, '+cash'))
    return transfer_id

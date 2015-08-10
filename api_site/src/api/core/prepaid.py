# -*- coding: utf-8 -*-
from ._bookkeeping import bookkeep, Event, SourceType
from ._dba import create_prepaid
from pytoolbox.util.dbe import transactional


@transactional
def prepaid(account_id, amount):
    prepaid_id = create_prepaid(account_id, amount)
    bookkeep(Event(SourceType.PREPAID, prepaid_id, amount),
             (account_id, '+asset'),
             (account_id, '+cash'))

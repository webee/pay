# -*- coding: utf-8 -*-
from tools.dbi import from_db

def list_all(account_id):
    return from_db().list("SELECT card_no, bank_name, bank_account_name, bank_account_type, reserved_phone, province, city "
                          "FROM virtual_account_bank_card WHERE account_id=%(account_id)s",
                            account_id=account_id)


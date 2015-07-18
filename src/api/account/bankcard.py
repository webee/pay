# -*- coding: utf-8 -*-
from api.util.attr_dict import AttrDict
from tools.dbi import from_db


def list_all_bankcards(account_id):
    return from_db().list("SELECT * FROM bankcard WHERE account_id=%(account_id)s", account_id=account_id)


def get_bankcard(account_id, bankcard_id):
    bankcard = from_db().get('SELECT * FROM bankcard WHERE account_id=%(account_id)s AND id=%(bankcard_id)s',
                             account_id=account_id, bankcard_id=bankcard_id)
    if bankcard:
        return _gen_bankcard_from_dict(bankcard)


def _gen_bankcard_from_dict(bankcard):
    return AttrDict(**bankcard)

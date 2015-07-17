# -*- coding: utf-8 -*-
from api.util.attr_dict import AttrDict
from tools.dbi import from_db


def get_user_bankcards(account_id):
    db = from_db()
    bankcards = db.list('select * from bankcard where account_id=%(account_id)s', account_id=account_id)

    return [_gen_bankcard_from_dict(bankcard) for bankcard in bankcards]


def get_bankcard(account_id, bankcard_id):
    db = from_db()
    bankcard = db.get('select * from bankcard where account_id=%(account_id)s and id=%(bankcard_id)s',
                      account_id=account_id, bankcard_id=bankcard_id)
    if bankcard:
        return _gen_bankcard_from_dict(bankcard)


def _gen_bankcard_from_dict(bankcard):
    return AttrDict(**bankcard)
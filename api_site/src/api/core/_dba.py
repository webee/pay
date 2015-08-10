# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from decimal import Decimal
from datetime import datetime

from ._bookkeeping import get_account_side_sign
from .util.oid import pay_id, withdraw_id, refund_id, transfer_id, prepaid_id
from pytoolbox.util.enum import enum
from pytoolbox.util.dbe import db_context


WITHDRAW_STATE = enum(FROZEN='FROZEN', SUCCESS='SUCCESS', FAILED='FAILED')
REFUND_STATE = enum(CREATED='CREATED', SUCCESS='SUCCESS', FAILED='FAILED')
BOOKKEEPING_SIDE = enum(CREDIT='CREDIT', DEBIT='DEBIT', BOTH='BOTH')
_BANK_ACCOUNT = enum(IsPrivateAccount=0, IsCorporateAccount=1)


@db_context
def get_user_cash_account_log(db, account_id, offset, limit):
    return db.list("""
                SELECT e.id, e.source_type, e.source_id, c.account_id, c.side, c.amount, c.created_on FROM cash_account_transaction_log c LEFT JOIN event e ON c.event_id=e.id
                  WHERE c.account_id=%(account_id)s
                  ORDER BY e.id DESC
                  LIMIT %(offset)s, %(limit)s
    """, account_id=account_id, offset=offset, limit=limit)


def _str_vars(params):
    return {'s': "'%s'", 'vars': params}


def _orig_vars(params):
    return {'s': "%s", 'vars': params}


def _gen_vars_str(sql, *args):
    strs = [','.join([arg['s']] * len(arg['vars'])) for arg in args]
    params = []
    for arg in args:
        params.extend(arg['vars'])

    return (sql % tuple(strs)) % tuple(params)


@db_context
def get_orders_info_by_ids(db, order_table, ids):
    return db.list(_gen_vars_str("""
                SELECT * FROM %s
                  WHERE id in (%s)""", _orig_vars([order_table]), _str_vars(ids)))


@db_context
def create_payment(db, trade_id, trade_info, payer_account_id, payee_account_id, amount):
    record_id = pay_id(payer_account_id)
    now = datetime.now()
    fields = {
        'id': record_id,
        'trade_id': trade_id,
        'trade_info': trade_info,
        'payer_account_id': payer_account_id,
        'payee_account_id': payee_account_id,
        'amount': amount,
        'created_on': now,
        'updated_on': now
    }
    db.insert('payment', **fields)
    return record_id


@db_context
def find_payment_by_id(db, id):
    return db.get('SELECT * FROM payment WHERE id = %(id)s', id=id)


@db_context
def find_payment_by_trade_id(db, trade_id):
    return db.get('SELECT * FROM payment WHERE trade_id = %(trade_id)s', trade_id=trade_id)


@db_context
def succeed_payment(db, id, paybill_id):
    now = datetime.now()
    db.execute(
        """
            UPDATE payment
              SET state = 'SUCCESS', transaction_ended_on = %(ended_on)s, paybill_id = %(paybill_id)s
              WHERE id = %(id)s
        """,
        id=id, paybill_id=paybill_id, ended_on=now)


@db_context
def fail_payment(db, _id):
    db.execute("UPDATE payment SET state = 'FAILED', transaction_ended_on = %(ended_on)s WHERE id = %(id)s",
               id=_id, ended_on=datetime.now())


@db_context
def create_transfer(db, trade_id, trade_info, payer_account_id, payee_account_id, amount):
    _id = transfer_id(payer_account_id)
    fields = {
        'id': _id,
        'trade_id': trade_id,
        'trade_info': trade_info,
        'payer_account_id': payer_account_id,
        'payee_account_id': payee_account_id,
        'amount': amount,
        'created_on': datetime.now()
    }
    db.insert('transfer', **fields)
    return _id


@db_context
def create_prepaid(db, account_id, amount):
    _id = prepaid_id(account_id)
    fields = {
        'id': _id,
        'account_id': account_id,
        'amount': amount,
        'created_on': datetime.now()
    }
    db.insert('prepaid', **fields)
    return _id


@db_context
def query_all_bankcards(db, account_id):
    return db.list("SELECT * FROM bankcard WHERE account_id=%(account_id)s", account_id=account_id)


@db_context
def create_bankcard(db, account_id, bankcard):
    fields = {
        'account_id': account_id,
        'card_no': bankcard.no,
        'card_type': bankcard.card_type,
        'account_name': bankcard.account_name,
        'flag': _BANK_ACCOUNT.IsCorporateAccount if bankcard.is_corporate_account else _BANK_ACCOUNT.IsPrivateAccount,
        'bank_code': bankcard.bank_code,
        'province_code': bankcard.province_code,
        'city_code': bankcard.city_code,
        'bank_name': bankcard.bank_name,
        'branch_bank_name': bankcard.branch_bank_name,
        'created_on': datetime.now()
    }
    return db.insert('bankcard', returns_id=True, **fields)


@db_context
def find_bankcard_by_id(db, bankcard_id):
    return db.get('SELECT * FROM bankcard WHERE id=%(bankcard_id)s', bankcard_id=bankcard_id)


@db_context
def create_withdraw(db, account_id, bankcard_id, amount, callback_url):
    _id = withdraw_id(account_id)
    fields = {
        'id': _id,
        'account_id': account_id,
        'bankcard_id': bankcard_id,
        'amount': amount,
        'created_on': datetime.now(),
        'async_callback_url': callback_url,
        'state': WITHDRAW_STATE.FROZEN
    }

    db.insert('withdraw', fields)
    return _id


@db_context
def transit_withdraw_state(db, _id, pre_state, new_state):
    return db.execute(
        """
            UPDATE withdraw
              SET state=%(new_state)s, updated_on=%(updated_on)s
              WHERE id=%(id)s and state=%(pre_state)s
        """,
        id=_id, pre_state=pre_state, new_state=new_state, updated_on=datetime.now()) > 0


@db_context
def find_withdraw_by_id(db, _id):
    return db.get('SELECT * FROM withdraw WHERE id=%(id)s', id=_id)


@db_context
def update_withdraw_result(db, _id, paybill_id, result, failure_info):
    return db.execute(
        """
          UPDATE withdraw
            SET paybill_id=%(paybill_id)s, result=%(result)s, failure_info=%(failure_info)s, updated_on=%(updated_on)s
            WHERE id=%(id)s AND state=%(state)s
        """,
        id=_id, state=WITHDRAW_STATE.FROZEN, result=result, paybill_id=paybill_id, failure_info=failure_info,
        updated_on=datetime.now()) > 0


@db_context
def list_all_unfailed_withdraw(db, account_id):
    return db.list(_sql_to_query_withdraw()
                   + " WHERE withdraw.state <> 'FAILED' AND withdraw.account_id = %(account_id)s"
                     " ORDER BY withdraw.created_on DESC",
                   account_id=account_id)


@db_context
def find_withdraw_basic_info_by_id(db, _id):
    return db.get(_sql_to_query_withdraw() + ' WHERE withdraw.id = %(withdraw_id)s', withdraw_id=_id)


@db_context
def create_refund(db, payment_id, payer_account_id, payee_account_id, amount, trade_info, created_on=datetime.now()):
    _id = refund_id(payer_account_id)
    fields = {
        'id': _id,
        'payment_id': payment_id,
        'payer_account_id': payer_account_id,
        'payee_account_id': payee_account_id,
        'amount': amount,
        'created_on': created_on,
        'state': REFUND_STATE.CREATED,
        'trade_info': trade_info
    }
    db.insert('refund', fields)
    return _id


@db_context
def update_refund_result(db, _id, refund_serial_no):
    return db.execute(
        """
            UPDATE refund
                SET refund_serial_no=%(refund_serial_no)s, updated_on=%(updated_on)s
                WHERE id=%(id)s
        """,
        id=_id, refund_serial_no=refund_serial_no, updated_on=datetime.now()) > 0


@db_context
def find_refund_by_id(db, id):
    return db.get('SELECT * FROM refund WHERE id=%(id)s', id=id)


@db_context
def transit_refund_state(db, _id, pre_state, new_state):
    return db.execute(
        """
            UPDATE refund
              SET state=%(new_state)s, updated_on=%(updated_on)s
              WHERE id=%(id)s and state=%(pre_state)s
        """,
        id=_id, pre_state=pre_state, new_state=new_state, updated_on=datetime.now()) > 0


@db_context
def get_settled_balance_and_last_id(db, account_id, account, side):
    settled_balance = db.get(
        """
          SELECT balance, last_transaction_log_id
            FROM account_balance
            WHERE account_id=%(account_id)s AND account=%(account)s AND side=%(side)s
        """,
        account_id=account_id, account=account, side=side)

    balance_value = Decimal(0)
    last_transaction_log_id = 0
    if settled_balance:
        balance_value = settled_balance['balance']
        last_transaction_log_id = settled_balance['last_transaction_log_id']

    return balance_value, last_transaction_log_id


@db_context
def get_unsettled_balance(db, account_id, account, side, low_id, high_id=None):
    account_table = account + "_account_transaction_log"
    if side == BOOKKEEPING_SIDE.BOTH:
        debit_sign, credit_sign = get_account_side_sign(account)
        if high_id is None:
            balance = db.get_scalar(
                """
                  SELECT SUM((CASE side WHEN 'debit' THEN %(debit_sign)s WHEN 'credit' THEN %(credit_sign)s END) * amount)
                    FROM """ + account_table + """
                    WHERE account_id=%(account_id)s and id > %(low_id)s
                """,
                debit_sign=debit_sign, credit_sign=credit_sign, account_id=account_id, low_id=low_id)
        else:
            balance = db.get_scalar(
                """
                  SELECT SUM((CASE side WHEN 'debit' THEN %(debit_sign)s WHEN 'credit' THEN %(credit_sign)s END) * amount)
                    FROM """ + account_table + """
                    WHERE account_id=%(account_id)s and id > %(low_id)s and id <= %(high_id)s
                """,
                debit_sign=debit_sign, credit_sign=credit_sign, account_id=account_id, low_id=low_id, high_id=high_id)
    else:
        if high_id is None:
            balance = db.get_scalar(
                """
                  SELECT SUM(amount)
                    FROM """ + account_table + """
                    WHERE account_id=%(account_id)s and side=%(side)s and id > %(low_id)s
                """,
                account_id=account_id, side=side, low_id=low_id)
        else:
            balance = db.get_scalar(
                """
                  SELECT SUM(amount)
                    FROM """ + account_table + """
                    WHERE account_id=%(account_id)s and side=%(side)s and id > %(low_id)s and id <= %(high_id)s
                """,
                account_id=account_id, side=side, low_id=low_id, high_id=high_id)

    return Decimal(0) if balance is None else balance


def _sql_to_query_withdraw():
    return """
        SELECT withdraw.id,
               concat(bank_name, '(', right(card_no, 4), ')') AS card,
               withdraw.created_on AS withdrawed_on,
               withdraw.amount as amount,
               if(withdraw.state = 'SUCCESS', withdraw.updated_on, null) AS received_on
        FROM withdraw
          INNER JOIN bankcard ON withdraw.bankcard_id = bankcard.id
    """
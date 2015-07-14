from datetime import datetime

from tools.dbi import from_db, transactional


def is_my_response(partner_oid):
    from api.base_config import lianlian_base_config as config
    return partner_oid == config.oid_partner


def is_valid_transaction(transaction_id, paid_amount):
    amount = from_db().get_scalar('SELECT amount FROM payment WHERE id = %(id)s AND success IS NULL',
                                  id=transaction_id)
    return amount == paid_amount


def is_successful_payment(pay_result):
    return pay_result.upper() == 'SUCCESS'


@transactional
def fail_transaction(transaction_id):
    from_db().execute('UPDATE payment SET success = 0, transaction_ended_on = %(ended_on)s WHERE id = %(id)s',
                      id=transaction_id, ended_on=datetime.now())


@transactional
def succeed_transaction(transaction_id, paybill_id):
    _update_payment(transaction_id, paybill_id)

    payment = from_db().get('SELECT payee_account_id, amount FROM payment WHERE id=%(id)s', id=transaction_id)
    amount = payment['amount']
    now = datetime.now()
    _log_transaction_into_secured_account(transaction_id, payment['payee_account_id'], amount, now)
    _charge_to_zyt_cash(amount, now)


def _update_payment(transaction_id, paybill_id):
    from_db().execute(
        """
            UPDATE payment SET success = 1, transaction_ended_on = %(ended_on)s, paybill_id=%(paybill_id)s
            WHERE id = %(id)s
        """,
        id=transaction_id, ended_on=datetime.now(), paybill_id=paybill_id)


def _log_transaction_into_secured_account(transaction_id, payee_account_id, amount, created_on):
    log = {
        'transaction_id': transaction_id,
        'type': 'PAY',
        'payee_account_id': payee_account_id,
        'amount': amount,
        'created_on': created_on
    }
    from_db().insert('secured_account_transaction_log', **log)


def _charge_to_zyt_cash(amount, created_on):
    entry = {
        'type': 'BORROW',
        'amount': amount,
        'created_on': created_on
    }
    from_db().insert('zyt_cash_transaction_log', **entry)






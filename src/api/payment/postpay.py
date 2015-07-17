from datetime import datetime

from api.constant import SourceType, WithdrawStep
from api.util.bookkeeping import bookkeeping, Event
from api.util.uuid import decode_uuid
from tools.dbi import from_db, transactional


def is_valid_transaction(transaction_id, uuid, paid_amount):
    if transaction_id != decode_uuid(uuid):
        return False

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
def succeed_transaction(payment_id, paybill_id):
    _update_payment(payment_id, paybill_id)

    payment = find_payment(payment_id)
    amount = payment['amount']
    bookkeeping(
        Event(payment['payee_account_id'], SourceType.WITHDRAW, WithdrawStep.FROZEN, payment_id, amount),
        '+secured', '+asset'
    )


def find_payment(transaction_id):
    return from_db().get('SELECT payee_account_id, amount FROM payment WHERE id=%(id)s', id=transaction_id)


def _update_payment(transaction_id, paybill_id):
    from_db().execute(
        """
            UPDATE payment SET success = 1, transaction_ended_on = %(ended_on)s, paybill_id=%(paybill_id)s
            WHERE id = %(id)s
        """,
        id=transaction_id, ended_on=datetime.now(), paybill_id=paybill_id)





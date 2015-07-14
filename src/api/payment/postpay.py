from datetime import datetime

from tools.dbi import from_db, transactional


def is_my_response(partner_oid):
    from api.base_config import lianlian_base_config as config
    return partner_oid == config.oid_partner


def is_valid_transaction(transaction_id, paid_amount):
    amount = from_db().get_scalar('SELECT amount FROM payment WHERE id = %(id)s AND success IS NOT NULL',
                                  id=transaction_id)
    return amount == paid_amount


def is_successful_payment(pay_result):
    return pay_result.upper() == 'SUCCESS'


@transactional
def fail_transaction(transaction_id):
    from_db().execute('UPDATE amount SET success = 0, transaction_ended_on = %(ended_on)s WHERE id = %(id)s',
                      id=transaction_id, ended_on=datetime.now())


@transactional
def succeed_transaction(transaction_id, paybill_id):
    from_db().execute(
        """
            UPDATE amount SET success = 1, transaction_ended_on = %(ended_on)s, paybill_id=%(paybill_id)s
            WHERE id = %(id)s
        """,
        id=transaction_id, ended_on=datetime.now(), paybill_id=paybill_id)
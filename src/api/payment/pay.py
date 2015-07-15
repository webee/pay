# -*- coding: utf-8 -*-
from api.util.ipay import transaction
from api.util.uuid import decode_uuid
from tools.dbi import from_db


def pay_by_uuid(payment_uuid):
    payment_id = decode_uuid(payment_uuid)
    payment = from_db().get(
        """
            SELECT payer_account_id, order_id, product_name, product_desc, amount, ordered_on, callback_url
              FROM payment
              WHERE id = %(id)s
        """,
        id=payment_id)
    return transaction.pay(
        payer_account_id=payment['payer_account_id'],
        order_no=payment_id,
        order_name=payment['product_name'],
        order_desc=payment['product_desc'],
        ordered_on=payment['ordered_on'],
        amount=payment['amount'],
        notification_url=payment['callback_url']
    )

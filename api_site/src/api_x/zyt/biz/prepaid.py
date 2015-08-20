# coding=utf-8
from api_x import db
from api_x.zyt.vas import bookkeep
from api_x.constant import TransactionState
from api_x.zyt.vas.models import EventType
from pytoolbox.util.dbs import transactional
from api_x.zyt.biz.models import TransactionType, PrepaidRecord
from api_x.zyt.biz.transaction import create_transaction, transit_transaction_state


@transactional
def create_prepaid(user_id, amount, pay_type, comments):
    transaction_record = create_transaction(TransactionType.PREPAID, amount, pay_type, comments, [user_id])

    prepaid_record = PrepaidRecord(transaction_id=transaction_record.id, sn=transaction_record.sn,
                                   user_id=user_id, amount=amount)
    db.session.add(prepaid_record)

    return prepaid_record


@transactional
def succeed_prepaid(vas_id, prepaid_record):
    if transit_transaction_state(prepaid_record.transaction_id, TransactionState.CREATED, TransactionState.SUCCESS):
        bookkeep(EventType.TRANSFER_IN, prepaid_record.sn, prepaid_record.user_id, vas_id, prepaid_record.amount)


@transactional
def fail_prepaid(prepaid_record):
    transit_transaction_state(prepaid_record.transaction_id, TransactionState.CREATED, TransactionState.FAILED)


def handle_payment_result(sn):
    pass


def handle_payment_notify(sn, vas_name, vas_sn):
    pass

# coding=utf-8
from api_x import db
from api_x.constant import TransactionState
from api_x.dbs import transactional
from .models import TransactionType, WithdrawRecord
from .transaction import create_transaction, transit_transaction_state
from ..vas.bookkeep import bookkeeping


@transactional
def create_refund(user_id, bankcard_id, amount, pay_type, comments):
    transaction_record = create_transaction(TransactionType.WITHDRAW, amount, pay_type, comments, [user_id])

    withdraw_record = WithdrawRecord(transaction_id=transaction_record.id, sn=transaction_record.sn,
                                     user_id=user_id, amount=amount, bankcard_id=bankcard_id)
    db.session.add(withdraw_record)

    freeze_cash(transaction_record.sn, user_id, amount)

    return withdraw_record


@transactional
def update_withdraw_info(withdraw_id, paybill_id, result, failure_info):
    withdraw_record = WithdrawRecord.query.get(withdraw_id)
    if withdraw_record is None:
        return None

    if paybill_id:
        withdraw_record.paybill_id = paybill_id
    if result:
        withdraw_record.result = result
    if failure_info:
        withdraw_record.failure_info = failure_info

    db.session.add(withdraw_record)

    return withdraw_record


@transactional
def succeed_withdraw(es_id, withdraw_record):
    if transit_transaction_state(withdraw_record.transaction_id, TransactionState.CREATED, TransactionState.SUCCESS):
        transfer_frozen_out(withdraw_record.sn, es_id, withdraw_record.user_id, withdraw_record.amount)
    else:
        raise Exception('error')


@transactional
def fail_withdraw(withdraw_record):
    if transit_transaction_state(withdraw_record.transaction_id, TransactionState.CREATED, TransactionState.FAILED):
        unfreeze_cash(withdraw_record.sn, withdraw_record.user_id, withdraw_record.amount)
    else:
        raise Exception('error')


# TODO
# notify

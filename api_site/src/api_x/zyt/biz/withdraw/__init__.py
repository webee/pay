# coding=utf-8
from api_x import db
from api_x.constant import TransactionState
from api_x.dbs import transactional
from api_x.zyt.biz.models import TransactionType, WithdrawRecord
from api_x.zyt.biz.transaction import create_transaction, transit_transaction_state
from api_x.zyt.vas.models import EventType
from api_x.zyt.vas.bookkeep import bookkeeping
from tools.mylog import get_logger


logger = get_logger(__name__)


def apply_to_withdraw(from_user_id,
                      flag_card, card_type, card_no, acct_name, bank_code, province_code,
                      city_code, bank_name, brabank_name, prcptcd,
                      amount, fee, client_notify_url, data):
    pass


@transactional
def _create_withdraw(from_user_id,
                     flag_card, card_type, card_no, acct_name, bank_code, province_code,
                     city_code, bank_name, brabank_name, prcptcd,
                     amount, fee, client_notify_url, data):
    # 计算相关金额
    actual_amount = amount
    # TODO
    comments = "提现至"
    tx_record = create_transaction(TransactionType.WITHDRAW, actual_amount, amount, comments, from_user_id)

    fields = {
        'tx_id': tx_record.id,
        'sn': tx_record.sn,
        'client_notify_url': client_notify_url
    }

    withdraw_record = WithdrawRecord(**fields)
    db.session.add(withdraw_record)

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

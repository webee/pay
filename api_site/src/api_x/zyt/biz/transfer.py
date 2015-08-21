# coding=utf-8
from api_x import db
from api_x.zyt.vas import bookkeep
from api_x.constant import TransactionState
from api_x.zyt.biz.models import TransactionType, TransferRecord
from api_x.zyt.vas.models import EventType
from api_x.zyt.vas import NAME
from api_x.zyt.biz.models import UserRole
from pytoolbox.util.dbs import transactional
from .vas import get_vas_by_name
from .transaction import create_transaction, transit_transaction_state


@transactional
def create_transfer(from_user_id, to_user_id, amount, pay_type, comments):
    transaction_record = create_transaction(TransactionType.TRANSFER, amount, pay_type, comments,
                                            [(from_user_id, UserRole.FROM), (to_user_id, UserRole.TO)])

    transfer_record = TransferRecord(transaction_id=transaction_record.id, sn=transaction_record.sn,
                                     from_user_id=from_user_id, to_user_id=to_user_id, amount=amount)
    db.session.add(transfer_record)

    zyt = get_vas_by_name(NAME)
    bookkeep(EventType.TRANSFER_OUT, transaction_record.sn, from_user_id, zyt.id, amount)

    if transit_transaction_state(transfer_record.transaction_id, TransactionState.CREATED, TransactionState.SUCCESS):
        bookkeep(EventType.TRANSFER_IN, transaction_record.sn, to_user_id, zyt.id, amount)

    return transfer_record

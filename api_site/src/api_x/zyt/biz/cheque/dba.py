# coding=utf-8
from sqlalchemy.orm import lazyload
from api_x.zyt.biz.models import ChequeRecord, Transaction
from api_x.constant import ChequeTxState
from datetime import datetime


def get_user_valid_cheques(user_id):
    return ChequeRecord.query.options(lazyload('tx')).outerjoin(Transaction).\
        filter(ChequeRecord.from_id == user_id).\
        filter(Transaction.state.in_([ChequeTxState.CREATED, ChequeTxState.FROZEN])).\
        filter(ChequeRecord.expired_at >= datetime.utcnow()).\
        order_by(Transaction.created_on.desc()).all()


def get_to_expire_cheques():
    return ChequeRecord.query.options(lazyload('tx')).outerjoin(Transaction).\
        filter(Transaction.state.in_([ChequeTxState.CREATED, ChequeTxState.FROZEN])).\
        filter(ChequeRecord.expired_at < datetime.utcnow()).all()

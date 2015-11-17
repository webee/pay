# coding=utf-8
from api_x.zyt.biz.models import Transaction, TransactionSnStack


def get_tx_by_id(transaction_id):
    return Transaction.query.get(transaction_id)


def get_tx_by_sn(sn, search_stack=False):
    tx = Transaction.query.filter_by(sn=sn).first()
    if tx is None and search_stack:
        sn_item = TransactionSnStack.query.filter_by(sn=sn).first()
        if sn_item is not None:
            tx = sn_item.tx
            tx.source_sn = sn_item.sn
            tx.source_sn_item = sn_item
    return tx


def get_tx_list(t, state):
    return Transaction.query.filter_by(type=t, state=state).all()

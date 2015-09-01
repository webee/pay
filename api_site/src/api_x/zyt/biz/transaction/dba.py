# coding=utf-8
from api_x.zyt.biz.models import Transaction


def get_tx_by_id(transaction_id):
    return Transaction.query.get(transaction_id)


def get_tx_by_sn(sn):
    return Transaction.query.filter_by(sn=sn).first()
# coding=utf-8
from api_x.zyt.biz.transaction.dba import get_tx_by_sn


def get_tx_prepaid_by_sn(sn):
    tx = get_tx_by_sn(sn)
    return tx, tx.record

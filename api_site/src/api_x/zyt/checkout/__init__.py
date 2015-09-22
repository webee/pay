# coding=utf-8
"""收银台"""
from __future__ import unicode_literals
from api_x.config import etc as config
from api_x.constant import TransactionType
from api_x.zyt.user_mapping import get_user_map_by_account_user_id


class PaymentEntity(object):
    def __init__(self, source, user_id, user_created_on, tx_sn, tx_created_on,
                 product_name, product_desc, amount):
        self.source = source
        self.user_id = user_id
        self.user_created_on = user_created_on
        self.tx_sn = tx_sn
        self.tx_created_on = tx_created_on
        self.product_name = product_name
        self.product_desc = product_desc
        self.amount = amount


def gen_payment_entity_by_pay_tx(tx):
    payment_record = tx.record

    user_map = get_user_map_by_account_user_id(payment_record.payer_id)
    user_id = '%s%s.%d' % (config.Biz.TX_SN_PREFIX, user_map.user_id, user_map.user_domain_id)

    return PaymentEntity(TransactionType.PAYMENT, user_id, user_map.created_on, tx.sn, tx.created_on,
                         payment_record.product_name, payment_record.product_desc,
                         payment_record.amount)


def gen_payment_entity_by_prepaid_tx(tx):
    prepaid_record = tx.record

    user_map = get_user_map_by_account_user_id(prepaid_record.to_id)
    user_id = '%s%s.%d' % (config.Biz.TX_SN_PREFIX, user_map.user_id, user_map.user_domain_id)

    return PaymentEntity(TransactionType.PREPAID, user_id, user_map.created_on, tx.sn, tx.created_on,
                         "充值", tx.comments,
                         prepaid_record.amount)

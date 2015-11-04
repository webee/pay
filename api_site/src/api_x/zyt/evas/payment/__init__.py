# coding=utf-8
from __future__ import unicode_literals
from api_x.constant import TransactionType
from api_x.zyt.user_mapping import get_user_map_by_account_user_id
from api_x.zyt.user_mapping.biz import gen_payment_user_id


class PaymentEntity(object):
    def __init__(self, source, user_id, user_created_on, tx_sn, tx_created_on,
                 product_name, product_desc, amount, order_id=None, channel_name=None):
        self.source = source
        self.user_id = user_id
        self.user_created_on = user_created_on
        self.tx_sn = tx_sn
        self.tx_created_on = tx_created_on
        self.product_name = product_name
        self.product_desc = product_desc
        self.amount = amount
        self.order_id = order_id
        self.channel_name = channel_name

    def dict(self):
        return {
            'order_id': self.order_id,
            'name': self.product_name,
            'desc': self.product_desc,
            'sn': self.tx_sn,
            'amount': self.amount,
            'created_on': self.tx_created_on
        }


def gen_payment_entity_by_pay_tx(tx):
    payment_record = tx.record

    user_map = get_user_map_by_account_user_id(payment_record.payer_id)
    user_id = gen_payment_user_id(user_map.user_id, user_map.user_domain_id)

    return PaymentEntity(TransactionType.PAYMENT, user_id, user_map.created_on, tx.sn, tx.created_on,
                         payment_record.product_name, payment_record.product_desc,
                         payment_record.amount, order_id=payment_record.order_id, channel_name=tx.channel_name)


def gen_payment_entity_by_prepaid_tx(tx):
    prepaid_record = tx.record

    user_map = get_user_map_by_account_user_id(prepaid_record.to_id)
    user_id = gen_payment_user_id(user_map.user_id, user_map.user_domain_id)

    return PaymentEntity(TransactionType.PREPAID, user_id, user_map.created_on, tx.sn, tx.created_on,
                         "充值", tx.comments,
                         prepaid_record.amount, channel_name=tx.channel_name)


def get_activated_evases(pay_scene, with_vas=False):
    from api_x.config import etc
    from api_x.zyt import vas

    evases = []

    if with_vas:
        evases.append(vas.NAME)

    for v in etc.Biz.PAYMENT_SCENE_VASES.get(pay_scene, []):
        if v in etc.Biz.ACTIVATED_EVAS:
            evases.append(v)
    return evases

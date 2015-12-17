# coding=utf-8
from __future__ import unicode_literals
from api_x.constant import TransactionType
from api_x.zyt.user_mapping import get_user_map_by_account_user_id
from api_x.zyt.user_mapping.biz import gen_payment_user_id


class PaymentEntity(object):
    def __init__(self, source, user_id, user_created_on, tx_sn, tx_created_on,
                 product_name, product_desc, amount, state, order_id=None, channel_name=None):
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
        self.state = state

    def dict(self):
        return {
            'order_id': self.order_id,
            'name': self.product_name,
            'desc': self.product_desc,
            'sn': self.tx_sn,
            'amount': self.amount,
            'created_on': self.tx_created_on
        }


def gen_payment_entity(tx):
    if tx.type == TransactionType.PAYMENT:
        return gen_payment_entity_by_pay_tx(tx)
    elif tx.type == TransactionType.PREPAID:
        return gen_payment_entity_by_prepaid_tx(tx)


def gen_payment_entity_by_pay_tx(tx):
    payment_record = tx.record

    user_map = get_user_map_by_account_user_id(payment_record.payer_id)
    user_id = gen_payment_user_id(user_map.user_id, user_map.user_domain_id)

    return PaymentEntity(TransactionType.PAYMENT, user_id, user_map.created_on, tx.sn, tx.created_on,
                         payment_record.product_name, payment_record.product_desc,
                         payment_record.amount, tx.state, order_id=payment_record.order_id, channel_name=tx.channel_name)


def gen_payment_entity_by_prepaid_tx(tx):
    prepaid_record = tx.record

    user_map = get_user_map_by_account_user_id(prepaid_record.to_id)
    user_id = gen_payment_user_id(user_map.user_id, user_map.user_domain_id)

    return PaymentEntity(TransactionType.PREPAID, user_id, user_map.created_on, tx.sn, tx.created_on,
                         "充值", tx.comments,
                         prepaid_record.amount, tx.state, channel_name=tx.channel_name)


def get_activated_evases(payment_scene, payment_entity, extra_params=None):
    from api_x.zyt.user_mapping.auth import vas_payment_is_enabled
    from api_x.config import etc
    from . import config

    extra_params = extra_params or {}
    evases = []

    pure_payment_scene = config.get_pure_payment_scene(payment_scene)
    vas_types = config.PAYMENT_SCENE_VASE_TYPES.get(pure_payment_scene, {})
    for v, t in vas_types.items():
        if not config.is_condition_pass(t, **extra_params):
            continue

        if v in etc.Biz.ACTIVATED_EVAS:
            if vas_payment_is_enabled(payment_entity, v):
                evases.append(v)

    if len(evases) <= 0:
        raise Exception("no payment type for [{0}]".format(payment_scene))

    evases = sorted(evases, key=lambda x: config.PAYMENT_TYPE_WEIGHTS.get(x, 100))
    return evases


def get_payment_type(payment_scene, vas_name, extra_params=None):
    from . import config

    extra_params = extra_params or {}
    pure_payment_scene = config.get_pure_payment_scene(payment_scene)
    vases_type = config.PAYMENT_SCENE_VASE_TYPES.get(pure_payment_scene, {})
    payment_type = vases_type.get(vas_name)
    payment_type = config.get_real_payment_type(payment_type, **extra_params)
    if payment_type is None:
        raise Exception("[{0}] is not support payment scene [{1}]".format(vas_name, payment_scene))
    return config.get_complex_payment_type(vas_name, payment_type, payment_scene)

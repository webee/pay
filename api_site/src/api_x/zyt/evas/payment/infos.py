# coding=utf-8
from __future__ import unicode_literals

from .config import VAS_INFOS
from . import get_activated_evases


def prepare(payment_scene, payment_entity, extra_params=None):
    data = {
        'state': payment_entity.state,
        'source': payment_entity.source,
        'sn': payment_entity.tx_sn,
        'created_on': payment_entity.tx_created_on,
        'name': payment_entity.product_name,
        'desc': payment_entity.product_desc,
        'amount': payment_entity.amount,
        'order_id': payment_entity.order_id
    }

    # FIXME: _ 表示不关心evases
    if payment_scene == '_':
        return data, None, None

    evases = get_activated_evases(payment_scene, payment_entity, extra_params)
    return data, evases, {vas: VAS_INFOS[vas] for vas in evases}

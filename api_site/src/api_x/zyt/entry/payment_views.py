# coding=utf-8
from __future__ import unicode_literals

from . import biz_entry_mod as mod
from api_x.utils.entry_auth import payment_entry
from api_x.constant import PaymentTxState
from api_x.utils import response
from api_x.zyt.evas.payment import gen_payment_entity_by_pay_tx, gen_payment_entity_by_prepaid_tx, get_activated_evases
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


@mod.route("/payment/<sn>/result", methods=["GET"])
@payment_entry
def pay_result(tx, sn):
    return response.success(state=tx.state)


@mod.route("/payment/<sn>/<payment_scene>/info", methods=["GET"])
@payment_entry
def info(tx, sn, payment_scene):
    return query_info(tx, payment_scene)


@mod.route("/payment/<sn>/<vas_name>/<payment_type>/param", methods=["GET"])
@payment_entry
def params(tx, sn, vas_name, payment_type):
    return prepare_params(tx, vas_name, payment_type)


def query_info(tx, payment_scene):
    from api_x.zyt.biz.models import TransactionType

    # TODO: log to db.
    logger.info("[PAYMENT INFO] {0}, {1}, {2}".format(payment_scene, tx.type, tx.sn))
    if tx.type == TransactionType.PAYMENT:
        payment_entity = gen_payment_entity_by_pay_tx(tx)
    elif tx.type == TransactionType.PREPAID:
        payment_entity = gen_payment_entity_by_prepaid_tx(tx)
    else:
        return response.bad_request()

    data = {
        'state': tx.state,
        'source': payment_entity.source,
        'sn': payment_entity.tx_sn,
        'created_on': payment_entity.tx_created_on,
        'name': payment_entity.product_name,
        'desc': payment_entity.product_desc,
        'amount': payment_entity.amount,
        'order_id': payment_entity.order_id
    }

    evases = get_activated_evases(payment_scene)
    if len(evases) <= 0:
        return response.fail(msg="no payment type for [{0}].".format(payment_scene))
    return response.success(info=data, activated_evas=evases)


def prepare_params(tx, vas_name, payment_type):
    from api_x.zyt.biz.models import TransactionType
    from api_x.zyt.evas.payment import params

    # TODO: log to db.
    logger.info("[PAYMENT PARAMS] {0}, {1}, {2}, {3}".format(vas_name, payment_type, tx.type, tx.sn))
    if tx.state != PaymentTxState.CREATED:
        return response.processed()

    if tx.type == TransactionType.PAYMENT:
        payment_entity = gen_payment_entity_by_pay_tx(tx)
    elif tx.type == TransactionType.PREPAID:
        payment_entity = gen_payment_entity_by_prepaid_tx(tx)
    else:
        return response.bad_request()

    try:
        prepared_params = params.prepare(vas_name, payment_type, payment_entity)
        return response.success(params=prepared_params)
    except Exception as e:
        return response.fail(msg=e.message)

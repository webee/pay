# coding=utf-8
from __future__ import unicode_literals

from . import biz_entry_mod as mod
from api_x.utils.entry_auth import payment_entry
from api_x.constant import PaymentTxState
from api_x.utils import response
from api_x.zyt.evas.payment import gen_payment_entity
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


@mod.route("/payment/<sn>/<payment_scene>/<vas_name>/param", methods=["GET"])
@payment_entry
def params(tx, sn, payment_scene, vas_name):
    return prepare_params(tx, payment_scene, vas_name)


def query_info(tx, payment_scene):
    from api_x.zyt.evas.payment import infos

    # TODO: log to db.
    logger.info("[PAYMENT INFO] {0}, {1}, {2}".format(payment_scene, tx.type, tx.sn))
    payment_entity = gen_payment_entity(tx)
    if payment_entity is None:
        return response.bad_request()

    try:
        data, evases = infos.prepare(payment_scene, payment_entity)
        return response.success(info=data, activated_evas=evases)
    except Exception as e:
        return response.fail(msg=e.message)


def prepare_params(tx, payment_scene, vas_name):
    from api_x.zyt.evas.payment import params

    # TODO: log to db.
    logger.info("[PAYMENT PARAMS] {0}, {1}, {2}, {3}".format(payment_scene, vas_name, tx.type, tx.sn))
    if tx.state != PaymentTxState.CREATED:
        return response.processed()

    payment_entity = gen_payment_entity(tx)
    if payment_entity is None:
        return response.bad_request()

    try:
        prepared_params = params.prepare(payment_scene, vas_name, payment_entity)
        return response.success(params=prepared_params)
    except Exception as e:
        return response.fail(msg=e.message)

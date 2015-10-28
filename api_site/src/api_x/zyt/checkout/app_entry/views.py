# coding=utf-8
from __future__ import unicode_literals

from api_x.constant import PaymentTxState
from . import app_checkout_entry_mod as mod
from api_x.utils import req, response
from .. import gen_payment_entity_by_pay_tx, gen_payment_entity_by_prepaid_tx, get_activated_evases
from api_x.constant import RequestClientType
from pytoolbox.util.log import get_logger
from api_x.utils.entry_auth import verify_request, checkout_entry


logger = get_logger(__name__)


@mod.route("/<source>/<sn>/info", methods=["GET"])
@checkout_entry()
def info(tx, source, sn):
    request_client_type = req.client_type()
    return query_info(source, tx, request_client_type)


@mod.route("/<source>/<sn>/<vas_name>/params", methods=["GET"])
@checkout_entry()
def params(tx, source, sn, vas_name):
    request_client_type = req.client_type()
    return prepare_params(source, tx, vas_name, request_client_type)


@mod.route("/pay/zyt/<sn>", methods=["POST"])
@verify_request('zyt_pay.app')
def zyt_pay(sn):
    """自游通余额支付入口，需要授权"""
    # TODO: 暂时以授权的方式进行，之后需要提供支付密码
    from api_x.zyt.biz.models import TransactionType
    from api_x.zyt import vas

    request_client_type = req.client_type()
    # is_success=True/False
    return prepare_params(TransactionType.PAYMENT, sn, vas.NAME, request_client_type)


def query_info(source, tx, request_client_type=RequestClientType.WEB):
    from api_x.zyt.biz.models import TransactionType

    # TODO: log to db.
    logger.info("[PAY INFO] {2}, {0}, {1}".format(source, tx.sn, request_client_type))
    if source == TransactionType.PAYMENT:
        payment_entity = gen_payment_entity_by_pay_tx(tx)
    elif source == TransactionType.PREPAID:
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

    evases = get_activated_evases(tx, is_wx_app=True)
    return response.success(info=data, activated_evas=evases)


def prepare_params(source, tx, vas_name, request_client_type=RequestClientType.WEB):
    from api_x.zyt.biz.models import TransactionType
    from api_x.zyt.checkout.app_entry import params

    # TODO: log to db.
    logger.info("[PAY PARAMS] {3}, {0}, {1}, {2}".format(source, tx.sn, vas_name, request_client_type))
    if tx.state != PaymentTxState.CREATED:
        return response.processed()
    if vas_name not in get_activated_evases(tx, is_wx_app=True, with_vas=True):
        return response.refused()

    if source == TransactionType.PAYMENT:
        payment_entity = gen_payment_entity_by_pay_tx(tx)
    elif source == TransactionType.PREPAID:
        payment_entity = gen_payment_entity_by_prepaid_tx(tx)
    else:
        return response.bad_request()

    try:
        prepared_params = params.prepare(vas_name, payment_entity)
        return response.success(params=prepared_params)
    except Exception as e:
        return response.fail(msg=e.message)

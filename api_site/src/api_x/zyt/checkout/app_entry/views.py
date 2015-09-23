# coding=utf-8
from __future__ import unicode_literals
from api_x.constant import PaymentTxState
from api_x.zyt.biz.transaction.dba import get_tx_by_sn

from api_x.config import etc as config
from . import app_checkout_entry_mod as mod
from api_x.utils import req, response
from .. import gen_payment_entity_by_pay_tx, gen_payment_entity_by_prepaid_tx
from pytoolbox.util.log import get_logger
from api_x.utils.entry_auth import verify_request


logger = get_logger(__name__)


@mod.route("/<source>/<sn>/<vas_name>/params", methods=["GET"])
def params(source, sn, vas_name):
    if vas_name not in config.Biz.ACTIVATED_EVAS:
        return response.not_found()

    request_client_type = req.client_type()
    logger.info("[PAY] {3}, {0}, {1}, {2}".format(source, sn, vas_name, request_client_type))

    return prepare_params(source, sn, vas_name)


def prepare_params(source, sn, vas_name):
    from api_x.zyt.biz.models import TransactionType
    from api_x.zyt.checkout.app_entry import params

    tx = get_tx_by_sn(sn)
    if tx is None:
        return response.not_found()
    if tx.state != PaymentTxState.CREATED:
        return response.bad_request()

    if source == TransactionType.PAYMENT:
        payment_entity = gen_payment_entity_by_pay_tx(tx)
    elif source == TransactionType.PREPAID:
        payment_entity = gen_payment_entity_by_prepaid_tx(tx)
    else:
        return response.bad_request()
    return params.prepare(vas_name, payment_entity)


@mod.route("/pay/zyt/<sn>", methods=["POST"])
@verify_request('zyt_pay.app')
def zyt_pay(sn):
    """自游通余额支付入口，需要授权"""
    # TODO: 暂时以授权的方式进行，之后需要单独的支付页面/密码
    from api_x.zyt.biz.models import TransactionType
    from api_x.zyt import vas

    request_client_type = req.client_type()
    # return do_pay(TransactionType.PAYMENT, sn, vas.NAME, request_client_type)

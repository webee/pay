# coding=utf-8
from __future__ import unicode_literals
from api_x.constant import PaymentTxState
from api_x.zyt.biz.transaction.dba import get_tx_by_sn

from flask import request
from api_x.config import etc as config
from . import app_checkout_entry_mod as mod
from pytoolbox.util.log import get_logger
from api_x.utils.entry_auth import verify_request, limit_referrer
from api_x.utils import req


logger = get_logger(__name__)


@mod.route("/pay/<source>/<sn>/<vas_name>", methods=["GET"])
def pay(source, sn, vas_name):
    return

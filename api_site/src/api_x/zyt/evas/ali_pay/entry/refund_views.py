# coding=utf-8
from __future__ import unicode_literals

from flask import request
from . import ali_pay_entry_mod as mod
from .commons import parse_and_verify
from . import notify_response
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


@mod.route("/refund/notify/<source>", methods=["POST"])
@parse_and_verify
def refund_notify(source):
    from ..notify import notify_refund
    data = request.verified_data

    resp_type = notify_refund(source, data)
    return notify_response.response(resp_type)

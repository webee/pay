# coding=utf-8
from __future__ import unicode_literals
from pytoolbox.util import strings
from api_x.config import zyt_pay
from pytoolbox.util.log import get_logger
from api_x.zyt.user_mapping.auth import add_sign_for_params


logger = get_logger(__name__)


def pay_param(sn):
    params = {
        'sn': sn,
        'nonce_str': strings.gen_rand_str(32),
        '_url': zyt_pay.Payment.WEB_URL
    }

    params = _append_sign(params)
    logger.info("request zyt pay WEB: {0}".format(params))

    return params


def _append_sign(params, keys=None):
    sign_params = params
    if keys is not None:
        sign_params = {k: params[k] for k in keys}
    return add_sign_for_params(zyt_pay.PAY_SITE_CHANNEL, sign_params)

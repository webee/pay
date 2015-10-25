# coding=utf-8
from __future__ import unicode_literals

from api_x.config import weixin_pay
from api_x.zyt.evas.error import InvalidSignError
from pytoolbox.util.log import get_logger
from ..error import RequestFaieldError
from pytoolbox.util.sign import SignType

logger = get_logger(__name__)


def generate_absolute_url(path):
    return weixin_pay.ROOT_URL + path


def is_success_request(data):
    ret = 'result_code' in data and data['result_code'] == 'SUCCESS'
    if not ret:
        msg = "request error: [{0}, {1}]".format(data.get('err_code'), data.get('err_code_des'))
        logger.error(msg)
        raise RequestFaieldError(msg)
    return ret


def append_md5_sign(app, params, keys=None):
    from . import signers

    sign_params = params
    if keys is not None:
        sign_params = {k: params[k] for k in keys}
    digest = signers[app].md5_sign(sign_params)
    params['sign'] = digest
    return params


def verify_sign(app, data):
    from . import signers

    sign_type = SignType.MD5
    if not signers[app].verify(data, sign_type):
        raise InvalidSignError(sign_type, data)
    return True
# coding=utf-8
from __future__ import unicode_literals

from api_x.config import weixin_pay
from pytoolbox.util.log import get_logger
from ..error import RequestFaieldError


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

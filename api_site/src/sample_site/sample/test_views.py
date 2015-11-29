# coding=utf-8
from __future__ import unicode_literals, print_function

from flask import request, jsonify
from . import sample_mod as mod
from sample_site import pay_client
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


@mod.route('/test/request/', methods=['GET', 'POST'])
def test_request():
    params = {k: v for k, v in request.values.items()}
    uri = params.get('uri', '/')
    url = pay_client.config.ROOT_URL + uri
    logger.info('uri: [{0}], params: [{1}]'.format(uri, params))
    if request.method == 'GET':
        result = pay_client.get_req(url, params)
    else:
        result = pay_client.post_req(url, params)

    if result:
        return jsonify(status_code=result.status_code, data=result.data), result.status_code
    return jsonify(result=None), 500

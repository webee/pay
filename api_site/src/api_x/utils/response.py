# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import Response, jsonify
from pytoolbox.util.log import get_logger

logger = get_logger(__name__)


def success(**kwargs):
    return jsonify(ret=True, **kwargs)


def _fail(code=1, msg='fail', **kwargs):
    logger.info(msg)
    return jsonify(ret=False, code=code, msg=msg, **kwargs)


def fail(code=1, msg='fail', **kwargs):
    return _fail(code, msg, **kwargs), 499


def bad_request(code=400, msg='bad request', **kwargs):
    return _fail(code, msg, **kwargs), code


def processed(code=202, msg='processed', **kwargs):
    return _fail(code, msg, **kwargs), code


def not_found(code=404, msg='not found.', **kwargs):
    return _fail(code, msg, **kwargs), code


def accepted(**kwargs):
    return success(**kwargs), 202


def refused(code=403, msg='refused', **kwargs):
    return _fail(code, msg, **kwargs), code


def expired(code=413, msg='expired', **kwargs):
    return _fail(code, msg, **kwargs), code


def submit_form(url, req_params, method='POST'):
    submit_page = '<form id="formName" action="{0}" method="{1}">'.format(url, method)
    for key in req_params:
        submit_page += '''<input type="hidden" name="{0}" value='{1}' />'''.format(key, req_params[key])
    submit_page += '<input type="submit" value="Submit" style="display:none" /></form>'
    submit_page += '<script>document.forms["formName"].submit();</script>'
    return Response(submit_page)

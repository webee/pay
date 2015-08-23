# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import Response, jsonify


def success(**kwargs):
    return jsonify(ret=True, **kwargs)


def fail(code=1, msg='fail', **kwargs):
    return jsonify(ret=False, code=code, msg=msg, **kwargs)


def bad_request(code=400, msg='bad request', **kwargs):
    return fail(code, msg, **kwargs), 400


def not_found(code=404, msg='not found.', **kwargs):
    return fail(code, msg, **kwargs), 404


def accepted(**kwargs):
    return success(**kwargs), 202


def refused(code=403, msg='refused', **kwargs):
    return fail(code, msg, **kwargs), 403


def submit_form(url, req_params):
    submit_page = '<form id="formName" action="{0}" method="POST">'.format(url)
    for key in req_params:
        submit_page += '''<input type="hidden" name="{0}" value='{1}' />'''.format(key, req_params[key])
    submit_page += '<input type="submit" value="Submit" style="display:none" /></form>'
    submit_page += '<script>document.forms["formName"].submit();</script>'
    return Response(submit_page)

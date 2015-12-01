# coding=utf-8
from __future__ import unicode_literals
from flask import render_template
from .utils import get_template


def payment_failed(result, client_type=None):
    if result is None:
        msg = "请求支付失败"
    elif result.status_code == 413:
        # 过期
        msg = "本支付链接已过期，请重新发起支付!"
    elif result.status_code == 404:
        msg = "交易号错误或者已失效，请重新发起支付!"
    elif result.status_code == 202:
        msg = "交易已支付，如果失败，请重新发起支付!"
    else:
        msg = "failed: code: {0}, msg: {1}".format(result.data['code'], result.data['msg'])
    return render_template(get_template("checkout/info", client_type), msg=msg)


def generate_submit_form(url, req_params, method='post', keep_all=False, excludes=set()):
    submit_page = '<meta http-equiv="content-type" content="text/html; charset=UTF-8">'
    submit_page += '<form id="payBillForm" action="{0}" method="{1}">'.format(url, method)
    for key in req_params:
        if key in excludes:
            continue
        if not keep_all and key.startswith('_'):
            continue
        submit_page += '''<input type="hidden" name="{0}" value='{1}' />'''.format(key, req_params[key])
    submit_page += '<input type="submit" value="Submit" style="display:none" /></form>'
    submit_page += '<script>document.forms["payBillForm"].submit();</script>'
    return submit_page

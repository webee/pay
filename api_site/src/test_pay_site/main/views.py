# coding=utf-8
from __future__ import unicode_literals, print_function

from flask import request, render_template, redirect, url_for, session, Response
from test_pay_site import config
from . import main_mod as mod
import requests
from test_pay_site.main.commons import generate_sn
from tools.mylog import get_logger


logger = get_logger(__name__)


@mod.route('/pay', methods=['POST'])
def pay():
    data = request.values
    merchant_id = data['merchant_id']
    order_no = data['order_no']

    sn = generate_sn(merchant_id, order_no)
    session[sn] = data

    return redirect(url_for('.pay_info', sn=sn))


@mod.route('/pay_info/<sn>', methods=['GET'])
def pay_info(sn):
    data = session[sn]

    merchant_id = data['merchant_id']
    user_id = data['user_id']
    order_no = data['order_no']
    product_name = data['product_name']
    amount = data['amount']
    return_url = data['return_url']
    notify_url = data['notify_url']

    res = {
        'sn': sn,
        'merchant': config.MERCHANTS_TABLE[merchant_id],
        'user_id': user_id,
        'order_no': order_no,
        'product_name': product_name,
        'amount': amount,
        'return_url': return_url,
        'notify_url': notify_url
    }
    return render_template('pay_info.html', res=res)


@mod.route('/do_pay', methods=['POST'])
def do_pay():
    sn = request.values['sn']
    result = request.values['result']
    data = session[sn]
    del session[sn]

    amount = data['amount']
    return_url = data['return_url']
    notify_url = data['notify_url']
    order_no = data['order_no']

    params = {
        'sn': sn,
        'result': result,
        'order_no': order_no,
        'amount': amount
    }

    # TODO: async notify
    try:
        logger.info('notify {0}: {1}'.format(notify_url, params))
        req = requests.post(notify_url, params)
        print(req.json())
    except Exception as e:
        print(e.message)

    return Response(generate_submit_form(return_url, params), status=200, mimetype='text/html')


def generate_submit_form(url, req_params):
    submit_page = '<form id="returnForm" action="{0}" method="POST">'.format(url)
    for key in req_params:
        submit_page += '''<input type="hidden" name="{0}" value='{1}' />'''.format(key, req_params[key])
    submit_page += '<input type="submit" value="Submit" style="display:none" /></form>'
    submit_page += '<script>document.forms["returnForm"].submit();</script>'
    return submit_page

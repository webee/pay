# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from flask import render_template, request, jsonify, url_for, redirect
from . import sample_mod as mod
from tools.mylog import get_logger
import requests
import json


logger = get_logger(__name__)


@mod.route('/accounts/<int:account_id>/withdraw', methods=['GET', 'POST'])
def withdraw(account_id):
    if request.method == 'GET':
        return render_template('withdraw.html', account_id=account_id)
    data = request.values
    amount = data['amount']
    params = {
        'bankcard_id': 1,
        'amount': amount,
        'callback_url': 'http://127.0.0.1:5001' + url_for('sample.withdraw_callback', account_id=account_id)
    }
    req = requests.post('http://127.0.0.1:5000/accounts/{0}/withdraw'.format(account_id), params)
    logger.info(req.content)

    if req.status_code >= 400:
        ret_data = req.json()
        return render_template('withdraw_result.html', account_id=account_id, error=ret_data['error'])

    return redirect(url_for('sample.withdraw', account_id=account_id))


@mod.route('/accounts/<int:account_id>/withdraw/callback', methods=['POST'])
def withdraw_callback(account_id):
    data = request.values

    logger.info('withdraw callback account_id={0}'.format(account_id))
    logger.info(json.dumps(data))

    return jsonify(ret=0)


@mod.route('/accounts/<int:account_id>/cash_balance', methods=['GET'])
def cash_balance(account_id):
    req = requests.get('http://127.0.0.1:5000/accounts/{0}/balance'.format(account_id))
    if req.status_code >= 400:
        return jsonify(balance=None)
    return jsonify(balance=req.json()['balance'])

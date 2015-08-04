# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from flask import render_template, request, jsonify, url_for, redirect, session, g, current_app
from . import withdraw_mod as mod
from tools.mylog import get_logger
import requests

logger = get_logger(__name__)

@mod.before_request
def set_current_channel():
    g.current_channel = 'withdraw'

@mod.route('/')
def withdraw():
    return redirect(url_for('.bind_card'))

@mod.route('/bind-card', methods= ['GET'])
def bind_card():
    return render_template('bind-card.html')


@mod.route('/<transaction_id>/result')
def show_withdraw_result_page(transaction_id):
    return render_template('show-withdraw-result.html')
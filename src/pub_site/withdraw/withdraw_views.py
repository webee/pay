# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from flask import render_template, request, jsonify, url_for, redirect
from . import withdraw_mod as mod
from tools.mylog import get_logger

logger = get_logger(__name__)

@mod.route('/withdraw/<transaction_id>/result')
def show_withdraw_result_page(transaction_id):
    return render_template('show-withdraw-result.html')
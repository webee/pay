# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from flask import render_template
from . import sample_mod as mod
from .trade.payment import pay as do_pay
from datetime import datetime

log = logging.getLogger(__name__)


@mod.route('')
def show_sample():
    return render_template('omnipotent.html')

@mod.route('/pay', methods=['POST'])
def pay():
    return _pay_one_cent()

def _pay_one_cent():
    return do_pay(
        user_id='user_0001',
        order_no='order_000001',
        ordered_on=datetime(2015, 3, 10, 10, 18, 0),
        order_name='Diablo III 1 account',
        order_desc='The account purchased to log on server in Taiwan',
        amount=0.01
    )

# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from flask import render_template
from . import account_mod as mod

log = logging.getLogger(__name__)


@mod.route('/<int:account_id>/bankcards', methods=['POST'])
def add_bankcard(account_id):
    return render_template('new_bankcard.html')

@mod.route('/<int:account_id>/bankcards/new')
def register_bankcard_info(account_id):
    return render_template('new_bankcard.html', account_id=account_id)

@mod.route('/<int:account_id>/withdraw')
def withdraw(account_id):
    return render_template('withdraw.html')

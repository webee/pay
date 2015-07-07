# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from flask import render_template
from . import account_mod as mod
from .services import bankcard
import logging

log = logging.getLogger(__name__)


@mod.route('/<int:account_id>/bankcards')
def list_bankcards(account_id):
    bankcards = bankcard.list_all(account_id)
    return render_template('bankcard_management.html', bankcards=bankcards)

@mod.route('/<int:account_id>/bankcards', methods=['POST'])
def add_bankcard(account_id):
    return render_template('new_bankcard.html')

@mod.route('/<int:account_id>/bankcards/new')
def register_bankcard_info(account_id):
    return render_template('new_bankcard.html')

@mod.route('/<int:account_id>/withdraw')
def withdraw(account_id):
    return render_template('withdraw.html')

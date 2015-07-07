# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from flask import render_template
import logging
from . import account_mod as mod

log = logging.getLogger(__name__)


@mod.route('/<int:account_id>/withdraw')
def withdraw(account_id):
    return render_template('withdraw.html')

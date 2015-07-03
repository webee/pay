# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from flask import render_template
import logging
from . import entry_mod as mod

log = logging.getLogger(__name__)


@mod.route('/')
def show_entry_page():
    return render_template('entry.html')

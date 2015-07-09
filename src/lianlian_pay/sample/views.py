# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

from flask import render_template
from . import sample_mod as mod

log = logging.getLogger(__name__)


@mod.route('/sample')
def show_sample():
    return render_template('omnipotent.html')

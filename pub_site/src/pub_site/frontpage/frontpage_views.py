# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging
from . import frontpage_mod as mod
from flask import g, render_template, redirect, url_for, flash

log = logging.getLogger(__name__)


@mod.route('/')
def show_frontpage():
    return render_template('frontpage/index.html')


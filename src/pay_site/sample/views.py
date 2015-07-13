# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from datetime import datetime

from flask import request, render_template, redirect, url_for, jsonify, current_app
from . import sample_mod as mod
from tools.utils import format_string
from tools.mylog import get_logger
import requests

logger = get_logger(__name__)


@mod.route('/pay/')
def pay():
    return render_template('pay.html')

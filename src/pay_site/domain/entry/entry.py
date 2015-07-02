# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from pay_op_site.domain import *
import logging
import datetime

log = logging.getLogger(__name__)

mod = Blueprint('entry', __name__, template_folder='', static_folder='static')

@mod.route('/entry')
def show_entry_page(name=None):
    return render_template('entry.html')

# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from pay_op_site.domain import *
import logging
import datetime

log = logging.getLogger(__name__)

mod = Blueprint('hello', __name__, template_folder='', static_folder='static')


@mod.route('/hello')
def show_hello_page(name=None):
    return render_template('hello.html', name=name)

@mod.route('/hello', methods=['POST'])
def say_hello():
    name = request.form['name']
    return show_hello_page(name)

@widget
@mod.route('/current_year')
def show_current_year_widget():
    current_year=datetime.datetime.today().year
    return render_template('show-current-year.html', current_year=current_year)




# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint

compatible_entry_mod = Blueprint('compatible_entry', __name__, template_folder='./templates')


from . import views

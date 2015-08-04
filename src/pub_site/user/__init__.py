# coding=utf-8
from __future__ import unicode_literals, print_function
from flask import Blueprint

user_mod = Blueprint('user', __name__, template_folder='./templates', static_folder='static')

from . import models, views

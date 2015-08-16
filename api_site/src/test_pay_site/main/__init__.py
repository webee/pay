# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint

main_mod = Blueprint('main', __name__)


from . import views

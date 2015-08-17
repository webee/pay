# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint

vas_entry_mod = Blueprint('vas_entry', __name__)

from . import views


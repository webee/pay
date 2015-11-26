# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint

system_entry_mod = Blueprint('system_entry', __name__)

from . import views

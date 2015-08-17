# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint

user_mapping_entry_mod = Blueprint('user_mapping_entry', __name__)

from . import views

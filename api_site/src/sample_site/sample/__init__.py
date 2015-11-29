# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint


sample_mod = Blueprint('sample', __name__)

from . import views, prepaid_views, test_views

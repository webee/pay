# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint


app_server_mod = Blueprint('app_server', __name__)

from . import views, prepaid_views

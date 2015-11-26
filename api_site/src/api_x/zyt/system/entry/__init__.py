# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint
from api_x.utils.entry_auth import GroupEntry

system_entry_mod = Blueprint('system_entry', __name__)
group = GroupEntry('system')

from . import views

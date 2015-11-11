# coding=utf-8
from __future__ import unicode_literals
from flask import Blueprint
from api_x.debit_note import sftp


debitnote_mod = Blueprint('debit_note', __name__)

from . import views

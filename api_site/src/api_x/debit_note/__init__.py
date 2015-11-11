# coding=utf-8
from __future__ import unicode_literals
from flask import Blueprint
from flask.ext.cors import CORS


debitnote_mod = Blueprint('debit_note', __name__)
CORS(debitnote_mod)


from . import views

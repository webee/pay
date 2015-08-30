# coding=utf-8
from flask import Blueprint

notify_mod = Blueprint('notify', __name__, static_folder='static')

from . import views

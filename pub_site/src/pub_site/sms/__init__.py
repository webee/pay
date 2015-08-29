# -*- coding: utf-8 -*-
from flask import Blueprint, g

sms_mod = Blueprint('sms', __name__)

from . import views

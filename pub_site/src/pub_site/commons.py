# coding=utf-8
from __future__ import unicode_literals
from decimal import Decimal
from flask.ext.login import current_user
from pub_site import pay_client
from wtforms.validators import StopValidation
from datetime import datetime
import random


def amount_less_than_balance(form, field):
    balance = pay_client.app_query_user_available_balance(current_user.user_id)
    if Decimal(field.data) > balance:
        raise StopValidation(u"提现金额不能超过账户余额")


def generate_order_id(user_id):
    return datetime.now().strftime("%Y%m%d%H%M%S%f") + str(user_id)[:7] + '%0.5d' % random.randint(0, 99999)

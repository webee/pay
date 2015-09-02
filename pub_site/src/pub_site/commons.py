# coding=utf-8
from __future__ import unicode_literals
from decimal import Decimal
from flask.ext.login import current_user
from pub_site import pay_client
import re
from wtforms import HiddenField
from wtforms.compat import string_types, text_type
from wtforms.validators import StopValidation
from datetime import datetime
import random


def amount_less_than_balance(form, field):
    balance = pay_client.app_query_user_available_balance(current_user.user_id)
    if Decimal(field.data) > balance:
        raise StopValidation(u"提现金额不能超过账户余额")


def generate_order_id(user_id):
    return datetime.now().strftime("%Y%m%d%H%M%S%f") + str(user_id)[:7] + '%0.5d' % random.randint(0, 99999)


class MyRegexp(object):
    def __init__(self, regex, flags=0, message=None):
        if isinstance(regex, string_types):
            regex = re.compile(regex, flags)
        self.regex = regex
        self.message = message

    def __call__(self, form, field, message=None):
        match = self.regex.match(str(field.data) or '')
        if not match:
            if message is None:
                if self.message is None:
                    message = field.gettext('Invalid input.')
                else:
                    message = self.message
            raise StopValidation(message)


class MyHiddenField(HiddenField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0]
        else:
            self.data = ''

    def _value(self):
        return text_type(self.data) if self.data is not None else ''
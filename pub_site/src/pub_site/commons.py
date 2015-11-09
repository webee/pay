# coding=utf-8
from __future__ import unicode_literals
from decimal import Decimal
from flask.ext.login import current_user
from flask.ext.wtf import Form
from pub_site import pay_client
from pub_site.sms import verification_code_manager
import re
from wtforms import HiddenField, ValidationError, StringField
from wtforms.compat import string_types, text_type
from wtforms.validators import StopValidation, DataRequired
from datetime import datetime
import random


def amount_less_than_balance(form, field):
    balance = pay_client.app_query_user_available_balance(current_user.user_id)
    if Decimal(field.data) > balance:
        raise StopValidation(u"提现金额不能超过账户余额")


def generate_order_id(user_id):
    return datetime.now().strftime("%y%m%d%H%M%S%f") + str(user_id)[:10] + '%0.4d' % random.randint(0, 9999)


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


def gen_verification_code_form(source):
    """生成带验证码的表单类"""
    def verification_code_should_match(form, field):
        user_id = current_user.user_id
        code = field.data

        if not verification_code_manager.check_verification_code(source, user_id, code):
            raise ValidationError(u"验证码错误")

    class VerificationCodeForm(Form):
        data_verified = HiddenField(u'data_verified', default=u"no")
        verification_code = StringField(u"验证码")
        verification_code_source = HiddenField(u'verification_code_source', default=source)
        request_verification_code = HiddenField(u'request_verification_code', default="no")

        def data_validate(self):
            # 是否为来自请求验证码按钮
            is_request = self.request_verification_code.data == 'yes'
            if not is_request:
                # 来自提交按钮
                self.verification_code.validators = [DataRequired(u"验证码不能为空"), verification_code_should_match]

            if self.validate():
                self.data_verified.data = 'yes'
            else:
                self.data_verified.data = 'no'
            return not is_request and self.data_verified.data == 'yes'

        def validate_on_submit(self):
            return self.is_submitted() and self.data_validate()
    return VerificationCodeForm
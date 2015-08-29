# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pub_site import config
from flask.ext.wtf import Form
from flask.ext.login import current_user
from wtforms import StringField, SelectField, SubmitField, HiddenField, FloatField, ValidationError
from wtforms.compat import text_type
from wtforms.validators import DataRequired, NumberRange, StopValidation
from decimal import Decimal
from . import dba
from pub_site.sms import verification_code_manager
import re
from wtforms.compat import string_types
from pub_site import pay_client


def card_number_should_be_legal(form, field):
    card_bin = pay_client.app_query_bin(field.data.replace(" ", ""))
    if not card_bin:
        raise ValidationError(u"无效的银行卡")
    card_type = card_bin['card_type']
    if card_type != 'DEBIT':
        raise ValidationError(u"银行卡必须为借记卡")


def card_is_not_in_use(form, field):
    uid = current_user.user_id
    bankcards = pay_client.app_list_user_bankcards(uid)

    for card in bankcards:
        if card['card_no'] == field.data:
            raise ValidationError(u"卡已绑定")


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
            is_request = self.request_verification_code.data == 'yes'
            if not is_request:
                self.verification_code.validators = [DataRequired(u"验证码不能为空"), verification_code_should_match]

            if self.validate():
                self.data_verified.data = 'yes'
            else:
                self.data_verified.data = 'no'
            return not is_request and self.data_verified.data == 'yes'

        def validate_on_submit(self):
            return self.is_submitted() and self.data_validate()
    return VerificationCodeForm


class BindCardForm(gen_verification_code_form(u'form-bind_card')):
    card_number = StringField(u"卡号",
                              validators=[DataRequired(u"卡号不能为空"), card_number_should_be_legal, card_is_not_in_use])
    name = StringField(u"开户姓名", validators=[DataRequired(u"姓名不能为空")])
    province = SelectField(u"省", coerce=str)
    city = SelectField(u"市", coerce=str)
    subbranch_name = StringField(u"开户支行", validators=[DataRequired(u"开户支行不能为空")])
    submit = SubmitField(u"提交")

    def __init__(self, *args, **kwargs):
        super(BindCardForm, self).__init__(*args, **kwargs)

        self.province.choices = [(key, value) for key, value in config.Data.PROVINCES.items()]
        if not self.is_submitted():
            self.province.data = self.province.choices[0][0]
        self.city.choices = [(key, value) for key, value in config.Data.CITIES[self.province.data].items()]
        if not self.is_submitted():
            self.city.data = self.city.choices[0][0]


class MyHiddenField(HiddenField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0]
        else:
            self.data = ''

    def _value(self):
        return text_type(self.data) if self.data is not None else ''


def amount_less_than_balance(form, field):
    balance = pay_client.app_query_user_available_balance(current_user.user_id)
    if Decimal(field.data) > balance:
        raise StopValidation(u"提现金额不能超过账户余额")


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


class WithdrawForm(gen_verification_code_form("form-withdraw")):
    bankcard = MyHiddenField()
    amount = FloatField(u"提现金额(元)",
                        validators=[DataRequired(u'请输入数字，小数点后最多2位， 例如"8.88"'), MyRegexp(r'^\d+(.\d{1,2})?$', message=u'请输入数字，小数点后最多2位， 例如"8.88"'),
                                    amount_less_than_balance,
                                    NumberRange(min=1, message=u"提现金额最少为1元")])
    submit = SubmitField(u"提交")

    def __init__(self, *args, **kwargs):
        super(WithdrawForm, self).__init__(*args, **kwargs)
        if not self.is_submitted():
            preferred_bankcard_id = dba.get_preferred_card_id(current_user.user_id)
            self.bankcard.data = preferred_bankcard_id or 0
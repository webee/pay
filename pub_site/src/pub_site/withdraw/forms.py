# -*- coding: utf-8 -*-

from datetime import datetime
import time

from pub_site import config
from flask.ext.wtf import Form
from flask.ext.login import current_user
from wtforms import StringField, SelectField, SubmitField, HiddenField, FloatField, ValidationError
from wtforms.compat import text_type
from wtforms.validators import DataRequired, NumberRange, StopValidation
import requests
from pytoolbox.util.dbe import from_db
from pay_client import PayClient
import re
from wtforms.compat import string_types
from . import WITHDRAW_COMMISSION


def name_and_id_card_should_match(form, field):
    url = '%s/api/leader?id=%s' % (config.Services.LEADER_SERVER, current_user.user_id)
    resp = requests.get(url)
    if resp.status_code != 200:
        raise ValidationError(u"持卡人信息与领队备案信息不一致")
    data = resp.json().get('data')
    if not data:
        raise ValidationError(u"持卡人信息与领队备案信息不一致")
    if data['contactsName'] != form.name.data or data['contactsIdcard'] != form.id_card_number.data:
        raise ValidationError(u"持卡人信息与领队备案信息不一致")


def identifying_code_should_match(form, field):
    now = datetime.fromtimestamp(time.time()).isoformat()
    sql = 'select code from identifying_code where user_id=%(user_id)s and expire_at>=%(now)s order by expire_at desc limit 1'
    code = from_db().get_scalar(sql, user_id=current_user.user_id, now=now)
    if code != field.data:
        raise ValidationError(u"验证码错误")


def card_number_should_be_legal(form, field):
    url = '%s/bankcards/%s/bin' % (config.PayAPI.ROOT_URL, field.data.replace(" ", ""))
    resp = requests.get(url)
    if resp.status_code != 200:
        raise ValidationError(u"无效的银行卡")
    card_type = resp.json().get('card_type')
    if card_type != 'DEBIT':
        raise ValidationError(u"银行卡必须为借记卡")


def card_is_not_in_use(form, field):
    result = PayClient().get_bankcards()
    if result['status_code'] == 200:
        for card in result['data']:
            if card['card_no'] == field.data:
                raise ValidationError(u"卡已绑定")


class BindCardForm(Form):
    card_number = StringField(u"卡号",
                              validators=[DataRequired(u"卡号不能为空"), card_number_should_be_legal, card_is_not_in_use])
    id_card_number = StringField(u"身份证号", validators=[DataRequired(u"身份证号不能为空"), name_and_id_card_should_match])
    name = StringField(u"姓名", validators=[DataRequired(u"姓名不能为空"), name_and_id_card_should_match])
    province = SelectField(u"省", coerce=str)
    city = SelectField(u"市", coerce=str)
    subbranch_name = StringField(u"开户支行", validators=[DataRequired(u"开户支行不能为空")])
    identifying_code = StringField(u"验证码", validators=[DataRequired(u"验证码不能为空"), identifying_code_should_match])
    submit = SubmitField(u"提交")

    def __init__(self, *args, **kwargs):
        Form.__init__(self)
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
    result = PayClient().get_balance()
    if result['status_code'] == 200:
        balance = result['data']['balance']
        if float(field.data) > balance:
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


class WithdrawForm(Form):
    bankcard = MyHiddenField()
    amount = FloatField(u"提现金额(元)",
                        validators=[DataRequired(u"请输入合法金额"), MyRegexp(r'^\d+(.\d{1,2})?$', message=u"请输入合法金额"),
                                    amount_less_than_balance,
                                    NumberRange(min=WITHDRAW_COMMISSION, message=u"提现金额不能少于2元(含手续费2元)")])
    identifying_code = StringField(u"验证码", validators=[DataRequired(u"验证码不能为空"), identifying_code_should_match])
    submit = SubmitField(u"提交")

    def __init__(self, *args, **kwargs):
        Form.__init__(self)
        if not self.is_submitted():
            preferred_bankcard_id = from_db().get_scalar(
                'select bankcard_id from preferred_card where user_id=%(user_id)s', user_id=current_user.user_id)
            self.bankcard.data = preferred_bankcard_id
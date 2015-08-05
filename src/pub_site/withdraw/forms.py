# -*- coding: utf-8 -*-

from datetime import datetime
import time

from pub_site import config
from flask.ext.wtf import Form
from flask.ext.login import current_user
from wtforms import StringField, SelectField, SubmitField, HiddenField, FloatField, ValidationError
from wtforms.compat import text_type
from wtforms.validators import DataRequired
import requests
from pytoolbox.util.dbe import from_db
from pay_client import PayClient


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
    sql = 'select count(1) from identifying_code where user_id=%(user_id)s and code=%(code)s and expire_at>=%(now)s'
    count = from_db().get_scalar(sql, user_id=current_user.user_id, code=field.data, now=now)
    if count == 0:
        raise ValidationError(u"验证码错误")


def card_number_should_be_legal(form, field):
    url = '%s/bankcards/%s/bin' % (config.PayAPI.ROOT_URL, field.data)
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
        province_data = config.Data.PROVINCES_AND_CITIES
        self.province.choices = [(pd['c'], p) for p, pd in province_data.items()]
        if not self.is_submitted():
            self.province.data = self.province.choices[0][0]
        province = province_data.get(self.province.choices[0][1])
        self.city.choices = [(cd['c'], c) for c, cd in province['cities'].items()]
        # if not self.is_submitted():
        self.city.data = self.city.choices[0][0]


class MyHiddenField(HiddenField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0]
        else:
            self.data = ''

    def _value(self):
        return text_type(self.data) if self.data is not None else ''


class WithdrawForm(Form):
    bankcard = MyHiddenField()
    amount = FloatField(u"提现金额(元)", validators=[DataRequired(u"提现金额不能为空")])
    identifying_code = StringField(u"验证码", validators=[DataRequired(u"验证码不能为空"), identifying_code_should_match])
    submit = SubmitField(u"提交")

    def __init__(self, *args, **kwargs):
        Form.__init__(self)
        if not self.is_submitted():
            preferred_bankcard_id = from_db().get_scalar(
                'select bankcard_id from preferred_card where user_id=%(user_id)s', user_id=current_user.user_id)
            self.bankcard.data = preferred_bankcard_id









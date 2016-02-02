# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from pub_site import config
from flask.ext.login import current_user
from pub_site.commons import amount_less_than_balance, MyRegexp, MyHiddenField, gen_verification_code_form
from wtforms import StringField, SelectField, SubmitField, DecimalField, ValidationError
from wtforms.validators import DataRequired, NumberRange
from . import dba
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


class WithdrawForm(gen_verification_code_form("form-withdraw")):
    bankcard = MyHiddenField()
    amount = DecimalField(u"提现金额(元)",
                          validators=[DataRequired(u'请输入数字，小数点后最多2位， 例如"8.88"'), MyRegexp(r'^\d+(.\d{1,2})?$', message=u'请输入数字，小数点后最多2位， 例如"8.88"'),
                                      amount_less_than_balance,
                                      NumberRange(min=Decimal(1), message=u"提现金额最少为1元")])
    submit = SubmitField(u"提交")

    def __init__(self, bankcards, *args, **kwargs):
        super(WithdrawForm, self).__init__(*args, **kwargs)
        if not self.is_submitted():
            preferred_bankcard_id = dba.get_preferred_card_id(current_user.user_id)
            self.bankcard.data = preferred_bankcard_id or bankcards[0]['id']

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask.ext.login import current_user
from flask.ext.wtf import Form
from wtforms import TextAreaField, SubmitField, DecimalField, RadioField
from wtforms.validators import DataRequired, NumberRange, Length, StopValidation
from pub_site.commons import MyRegexp
from pub_site import pay_client
from decimal import Decimal


def amount_less_than_balance(form, field):
    if form.pay_channel.data == 'ZYT':
        balance = pay_client.app_query_user_available_balance(current_user.user_id)
        if Decimal(field.data) > balance:
            raise StopValidation(u"支付金额不能超过账户余额")


class PayToLvyeForm(Form):
    amount = DecimalField(u"金额(元)",
                          validators=[DataRequired(u'请输入数字，小数点后最多2位， 例如"8.88"'),
                                      MyRegexp(r'^\d+(.\d{1,2})?$', message=u'请输入数字，小数点后最多2位， 例如"8.88"'),
                                      amount_less_than_balance,
                                      NumberRange(min=Decimal('0.01'), message=u'金额必须为大于0')])
    pay_channel = RadioField(u"付款方式", choices=[('LVYE_PAY', '绿野在线支付'), ('ZYT', '自游通余额')],
                             validators=[DataRequired(u"请选择支付方式")], default='BANKCARD')
    comment = TextAreaField(u"备注", validators=[DataRequired(u"请提供备注信息"), Length(max=150, message=u"备注不能超过150个字")])
    submit = SubmitField(u"确认")
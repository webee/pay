# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask.ext.wtf import Form
from wtforms import TextAreaField, SubmitField, DecimalField, RadioField
from wtforms.validators import DataRequired, NumberRange, Length


class PayToLvyeForm(Form):
    amount = DecimalField(u"金额(元)",
                          validators=[DataRequired(u'请输入数字，小数点后最多2位， 例如"8.88"'),
                                      NumberRange(min=0.01, message=u'请输入数字，小数点后最多2位， 例如"8.88"')])
    pay_channel = RadioField(u"付款方式", choices=[('BANKCARD', '快捷支付'), ('ZYT', '自游通余额')],
                             validators=[DataRequired(u"请选择支付方式")], default='BANKCARD')
    comment = TextAreaField(u"备注", validators=[DataRequired(u"请提供备注信息"), Length(max=150, message=u"备注不能超过150个字")])
    submit = SubmitField(u"确认")
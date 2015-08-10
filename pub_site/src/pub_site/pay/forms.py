# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import FloatField, RadioField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from .import PayType





class PayForm(Form):
    amount = FloatField(u"付款金额(元)", validators=[DataRequired(u"请输入合法金额"), NumberRange(min=0.01, message=u"请输入合法金额")])
    pay_type = RadioField(u"选择付款方式", coerce=int, choices=[(PayType.BY_BALANCE, u"账户余额支付"), (PayType.BY_BANKCARD, u"银行卡支付")],
                          default=PayType.BY_BALANCE)
    comment = TextAreaField(u"支付备注", validators=[DataRequired(u"请提供备注信息")])
    submit = SubmitField(u"确认")



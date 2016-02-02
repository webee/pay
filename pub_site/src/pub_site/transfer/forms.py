# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from flask.ext.wtf import Form
from pub_site.commons import amount_less_than_balance, MyRegexp
from wtforms import StringField, SubmitField, ValidationError, DecimalField
from wtforms.validators import DataRequired, NumberRange, Length
from pub_site import dba


def username_should_exists(form, field):
    username = field.data
    if not dba.is_username_exists(username):
        raise ValidationError(u"用户不存在")


class TransferForm(Form):
    username = StringField(u"用户名", validators=[DataRequired(u"用户名不能为空"), username_should_exists])
    amount = DecimalField(u"转账金额(元)",
                          validators=[DataRequired(u'请输入数字，小数点后最多2位， 例如"8.88"'), MyRegexp(r'^\d+(.\d{1,2})?$', message=u'请输入数字，小数点后最多2位， 例如"8.88"'),
                                      amount_less_than_balance,
                                      NumberRange(min=Decimal(0.01), message=u"提现金额必须大于0")])
    info = StringField(u"备注", validators=[Length(max=50, message=u"备注不能超过50个字")])
    submit = SubmitField(u"提交")

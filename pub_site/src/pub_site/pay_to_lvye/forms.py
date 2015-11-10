# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask.ext.wtf import Form
from wtforms import TextAreaField, SubmitField, DecimalField
from wtforms.validators import DataRequired, NumberRange, Length
from pub_site.commons import MyRegexp
from decimal import Decimal


class PayToLvyeForm(Form):
    amount = DecimalField(u"金额(元)",
                          validators=[DataRequired(u'请输入数字，小数点后最多2位， 例如"8.88"'),
                                      MyRegexp(r'^\d+(.\d{1,2})?$', message=u'请输入数字，小数点后最多2位， 例如"8.88"'),
                                      NumberRange(min=Decimal('0.01'), message=u'金额必须为大于0')])
    comment = TextAreaField(u"备注", validators=[DataRequired(u"请提供备注信息"), Length(max=150, message=u"备注不能超过150个字")])
    submit = SubmitField(u"确认")
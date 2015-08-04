# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class BindCardForm(Form):
    card_number = StringField(u"卡号", validators=[DataRequired(u"卡号不能为空")])
    id_card_number = StringField(u"身份证号", validators=[DataRequired(u"身份证号不能为空")])
    name = StringField(u"姓名", validators=[DataRequired(u"姓名不能为空")])
    identifying_code = StringField(u"验证码", validators=[DataRequired(u"验证码不能为空")])
    submit = SubmitField(u"提交")

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        return True

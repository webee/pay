# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LvyeCorpLoginForm(Form):
    username = StringField("用户名", validators=[DataRequired(u"用户名不能为空")])
    password = PasswordField(u"密码", validators=[DataRequired(u"密码不能为空")])
    submit = SubmitField(u"登录")

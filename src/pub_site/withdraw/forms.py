# -*- coding: utf-8 -*-

from pub_site import config
from flask import url_for
from flask.ext.wtf import Form
from flask.ext.login import current_user
from wtforms import StringField, SelectField, SubmitField, ValidationError
from wtforms.validators import DataRequired
import requests
from pytoolbox.util.dbe import from_db
from datetime import datetime
import time


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


class BindCardForm(Form):
    card_number = StringField(u"卡号", validators=[DataRequired(u"卡号不能为空")])
    id_card_number = StringField(u"身份证号", validators=[DataRequired(u"身份证号不能为空"), name_and_id_card_should_match])
    name = StringField(u"姓名", validators=[DataRequired(u"姓名不能为空"), name_and_id_card_should_match])
    province = SelectField(u"省")
    city = SelectField(u"市")
    subbranch_name = StringField(u"开户支行", validators=[DataRequired(u"开户支行不能为空")])
    identifying_code = StringField(u"验证码", validators=[DataRequired(u"验证码不能为空"), identifying_code_should_match])
    submit = SubmitField(u"提交")

    def __init__(self, *args, **kwargs):
        Form.__init__(self)
        province_data = config.Data.PROVINCES_AND_CITIES
        self.province.choices = [(pd['c'], p) for p, pd in province_data.items()]
        self.province.data = self.province.choices[0]
        province = province_data.get(self.province.data[1])
        self.city.choices = [(cd['c'], c) for c, cd in province['cities'].items()]
        self.city.data = self.city.choices[0]





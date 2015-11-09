# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from wtforms import SubmitField
from pub_site.commons import gen_verification_code_form


class ZytPayForm(gen_verification_code_form("form-zyt_pay")):
    submit = SubmitField(u"确认支付")

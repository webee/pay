# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime, timedelta
import string

from pub_site.sms import sms
from pytoolbox.util.dbs import transactional
from pytoolbox.util import strings
from pub_site.models import VerificationCode
from pub_site import db


def generate_and_send_verification_code(source, user_id, phone_no):
    _clear_expired_verification_code()
    code = _generate_verification_code(source, user_id)
    msg = _build_message(code)
    return sms.send(phone_no, msg)


@transactional
def _clear_expired_verification_code():
    VerificationCode.query.\
        filter(VerificationCode.expire_at < datetime.utcnow()).\
        delete()

@transactional
def _generate_verification_code(source, user_id):
    verification_code = VerificationCode.query.filter_by(source=source, user_id=user_id).first()
    if verification_code is None:
        code = strings.gen_rand_str(6, string.digits)
        expire_at = datetime.utcnow() + timedelta(minutes=5)

        verification_code = VerificationCode(source=source, user_id=user_id, code=code, expire_at=expire_at)
    else:
        # 延长一分钟
        verification_code.expire_at += timedelta(minutes=1)
    db.session.add(verification_code)

    return verification_code.code


def _build_message(code):
    return u"【绿野】验证码%s，该验证码五分钟内有效。" % code

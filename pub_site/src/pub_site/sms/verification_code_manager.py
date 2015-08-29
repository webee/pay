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


def check_verification_code(source, user_id, code):
    verification_code = VerificationCode.query.filter_by(source=source, user_id=user_id).first()

    if verification_code is None:
        return False

    now = datetime.utcnow()
    expire_at = verification_code.expire_at
    real_code = verification_code.code
    if now > expire_at or real_code == code:
        # 过期或者验证通过则删除该验证码
        _delete_verification_code(verification_code)
    return real_code == code


@transactional
def _delete_verification_code(verification_code):
    db.session.delete(verification_code)


@transactional
def _clear_expired_verification_code():
    VerificationCode.query.\
        filter(VerificationCode.expire_at < datetime.utcnow()).\
        delete()


@transactional
def _generate_verification_code(source, user_id):
    verification_code = VerificationCode.query.filter_by(source=source, user_id=user_id).first()
    if verification_code is None:
        verification_code = VerificationCode(source=source, user_id=user_id)

    code = strings.gen_rand_str(6, string.digits)
    expire_at = datetime.utcnow() + timedelta(minutes=5)
    verification_code.code = code
    verification_code.expire_at = expire_at

    db.session.add(verification_code)

    return verification_code.code


def _build_message(code):
    return "验证码%s，该验证码五分钟内有效。" % code

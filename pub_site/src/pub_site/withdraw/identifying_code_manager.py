# -*- coding: utf-8 -*-

import requests
import string
import random
import time
from datetime import datetime
from pub_site import config
from flask.ext.login import current_user
from pytoolbox.util.dbs import from_db


def generate_and_send_identifying_code():
    _clear_expired_identifying_code()
    mobile = _get_user_contact_mobile()
    # mobile = u"13522919293"
    identifying_code = _generate_identifying_code()
    message = _build_message(identifying_code)
    return _send_message(mobile, message)


def _clear_expired_identifying_code():
    now = datetime.fromtimestamp(time.time()).isoformat()
    from_db().execute("delete from identifying_code where user_id=%(user_id)s and expire_at<%(now)s",
                      user_id=current_user.user_id, now=now)


def _send_message(mobile, messages):
    return requests.post(config.SMSConfig.URL, data={
        'cdkey': config.SMSConfig.CD_KEY,
        'password': config.SMSConfig.PASSWORD,
        'phone': mobile,
        'message': messages
    })


def _get_user_contact_mobile():
    url = '%s/api/leader?id=%s' % (config.Services.LEADER_SERVER, current_user.user_id)
    resp = requests.get(url)
    if resp.status_code != 200:
        return -1
    data = resp.json().get('data')
    return data["contactsMobile"] if data else -1


def _generate_identifying_code():
    identifying_code = string.join(random.sample('0123456789', 6)).replace(" ", "")
    expire_at = datetime.fromtimestamp(time.time() + 300).isoformat()
    record = {
        "code": identifying_code,
        "user_id": current_user.user_id,
        "expire_at": expire_at
    }
    from_db().insert("identifying_code", record)
    return identifying_code


def _build_message(identifying_code):
    return u"【绿野】尊敬的用户，您的验证码是%s，请输入以进行身份认证。该验证码五分钟内有效。" % identifying_code



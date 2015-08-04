# -*- coding: utf-8 -*-

import requests
import string
import random
import time
from datetime import datetime
from pub_site import config
from flask.ext.login import current_user
from pytoolbox.util.dbe import from_db


SMS = {
    'url': 'http://sdk999ws.eucp.b2m.cn:8080/sdkproxy/sendsms.action',
    'cdkey': '9SDK-EMY-0999-JBQOO',
    'password': '506260',
}


def generate_and_send():
    mobile = _get_user_contact_mobile()
    # mobile = u"13522919293"
    identifying_code = _generate_identifying_code()
    message = _build_message(identifying_code)
    return _send_message(mobile, message)


def _send_message(mobile, messages):
    msg = messages
    resp = requests.post(
        SMS['url'],
        data={'cdkey': SMS['cdkey'],
              'password': SMS['password'],
              'phone': mobile,
              'message': msg}
    )
    return resp


def _get_user_contact_mobile():
    url = '%s/api/leader?id=%s' % (config.Services.LEADER_SERVER, current_user.user_id)
    resp = requests.get(url)
    if resp.status_code != 200:
        return -1
    data = resp.json().get('data')
    if not data:
        return -1
    return data["contactsMobile"]


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



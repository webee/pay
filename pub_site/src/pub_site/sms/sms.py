# coding=utf-8
from __future__ import unicode_literals

from bs4 import BeautifulSoup
from pub_site import config
import requests
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


def send(phone_no, msg):
    msg = _build_message(msg)
    print(msg)
    req = requests.post(config.SMSConfig.URL, data={
        'cdkey': config.SMSConfig.CD_KEY,
        'password': config.SMSConfig.PASSWORD,
        'phone': phone_no,
        'message': msg
    })

    if req.status_code != 200:
        return False

    try:
        bs = BeautifulSoup(req.content.strip(), 'html.parser')
        return bs.response.error.text == '0'
    except Exception as e:
        logger.exception(e)

    return False


def _build_message(msg):
    if config.IS_PROD:
        return "【绿野】%s" % msg
    # FIXME.
    return "【绿野】%s" % msg

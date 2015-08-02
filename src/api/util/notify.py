# coding=utf-8
from tools.mylog import get_logger
import json


logger = get_logger(__name__)


def notify_client(url, params):
    import requests

    try:
        req = requests.post(url, params)
        if req.status_code == 200:
            data = req.json()
            if data['code'] == 0:
                if data['message'] != "OK":
                    # TODO
                    # log it.
                    logger.warn('notify [{0}, {1}] failed.'.format(url, json.dumps(params)))
                    pass
                return True
    except:
        return False

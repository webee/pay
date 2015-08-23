# -*- coding: utf-8 -*-
from functools import wraps
from flask import request
from api_x.utils import response
from pytoolbox.util.sign import Signer
from api_x.zyt.user_mapping import get_channel_by_name
from api_x.config import etc as config


def verify_request(entry_name):
    def do_verify_request(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                data = request.values
                channel_name = data['channel_name']
                channel = get_channel_by_name(channel_name)
                if not channel.has_entry_perm(entry_name):
                    return response.refused()

                sign_type = data['sign_type']
                signer = Signer('key', 'sign', channel.md5_key, config.LVYE_PRI_KEY, channel.public_key)
                if not signer.verify(data, sign_type):
                    return response.refused()
            except Exception as e:
                return response.bad_request(msg=e.message)
            return f(*args, **kwargs)
        return wrapper
    return do_verify_request

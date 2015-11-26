# coding=utf-8
from __future__ import unicode_literals

from api_x.config import etc as config
from flask import jsonify
from . import main_entry as mod
import time
from pytoolbox.util import public_key, strings


@mod.route('/ping')
def ping():
    return jsonify(env=config.__env_name__,
                   host_url=config.HOST_URL,
                   t=time.time())


@mod.route('/keys_gen')
def keys_gen():
    md5_key_str = strings.gen_rand_str(32)

    channel_pri_key = public_key.generate_key()
    channel_pub_key = channel_pri_key.gen_public_key()
    channel_pri_key_str = channel_pri_key.b64encoded_binary_key_data()
    channel_pub_key_str = channel_pub_key.b64encoded_binary_key_data()
    return jsonify(MD5_KEY=md5_key_str,
                   CHANNEL_PRI_KEY=channel_pri_key_str,
                   CHANNEL_PUB_KEY=channel_pub_key_str)

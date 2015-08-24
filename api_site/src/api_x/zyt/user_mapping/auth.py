# coding=utf-8
from api_x.config import etc as config
from api_x.zyt.user_mapping import get_channel_by_name
from pytoolbox.util.sign import SignType, Signer


def add_sign_for_params(channel_name, params, sign_type=SignType.RSA):
    channel = get_channel_by_name(channel_name)

    signer = Signer('key', 'sign', channel.md5_key, config.LVYE_PRI_KEY, channel.public_key)
    params['channel_name'] = channel_name
    params['sign_type'] = sign_type
    params['sign'] = signer.sign(params, sign_type)

    return params

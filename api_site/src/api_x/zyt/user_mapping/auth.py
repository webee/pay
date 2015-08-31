# coding=utf-8
from api_x.config import etc as config
from api_x.zyt.user_mapping import get_channel_by_name
from pytoolbox.util.sign import SignType, Signer
from pytoolbox.util import public_key, aes
from pytoolbox.util.strings import gen_rand_str


def add_sign_for_params(channel_name, params, sign_type=SignType.RSA):
    if params is None:
        return params

    channel = get_channel_by_name(channel_name)

    # 这里的主要作用是签名，只需要lvye_pri_key或md5_key
    signer = Signer('key', 'sign', channel.md5_key, config.LVYE_PRI_KEY, None)
    # 用来加密lvye_pub_key
    channel_pub_key = public_key.loads_b64encoded_key(channel.public_key)
    params['channel_name'] = channel_name
    params['sign_type'] = sign_type
    params['sign'] = signer.sign(params, sign_type)
    # 每次动态生成此密码
    lvye_aes_key = gen_rand_str(16)
    params['_lvye_pub_key'] = aes.encrypt_to_base64(config.LVYE_PUB_KEY, lvye_aes_key)
    params['_lvye_aes_key'] = channel_pub_key.encrypt_to_base64(lvye_aes_key)

    return params

# coding=utf-8
import json
import base64
from Crypto.Cipher import AES
import digest

def __pkcs7_padding(data, size=16):
    """补足被解密串到单位长度的位数
    :param data: 被加密串
    :param size: 单位长度
    :return:
    """
    length = size - len(data) % size
    return data + chr(length) * length


def __depkcs7_padding(data, size=16):
    """移除解密出的字符串的padding
    :param data: 解密出的字符串
    :param size: 单位长度
    :return:
    """
    newdata = data[:-size]
    for c in data[-size:]:
        if ord(c) > size:
            newdata += c
    return newdata

    # length = ord(data[-1])
    # if length < size and data[-length:] == data[-1] * length:
    #     # check是否为paddding
    #     return data[:-length]
    # return data


def encrypt_to_base64(data, key):
    data = data.encode('utf8')
    cipher = AES.new(key)
    return base64.urlsafe_b64encode(cipher.encrypt(__pkcs7_padding(data)))


def decrypt_from_base64(data, key):
    cipher = AES.new(key)
    return __depkcs7_padding(cipher.decrypt(base64.urlsafe_b64decode(data))).decode('utf8')


def get_hmac(arr, key):
    return digest.hmac_sign(''.join(arr), key)


def get_data_hmac(data, key):
    d = data.items()
    d.sort()

    string_array = [v for k, v in d if k != 'hmac']
    return get_hmac(string_array, key)


def encrypt_data(data, key):
    data_map = {k: v for k, v in data.items()}

    # key_for_hmac = key
    key_for_aes = key[:16]

    # hmac = get_data_hmac(data_map, key_for_hmac)

    # data_map['hmac'] = hmac
    data_json_string = json.dumps(data_map)
    data = encrypt_to_base64(data_json_string, key_for_aes)

    return data


def decrypt_data(data, key):
    # key_for_hmac = key
    key_for_aes = key[:16]

    try:
        decrypted_data = decrypt_from_base64(data, key_for_aes)
        result = json.loads(decrypted_data)

        # hmac_ret = result['hmac']
        # hmac = get_data_hmac(result, key_for_hmac)
    except Exception as e:
        raise ValueError("decrypt error: %s" % e.message)

    # if hmac_ret != hmac:
    #     raise ValueError("hmac mismatch.")

    return result

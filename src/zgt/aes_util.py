# coding=utf-8
from __future__ import print_function, unicode_literals
from Crypto.Cipher import AES

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


def encrypt(data, key):
    """
    加密
    :param data: 待加密内容
    :param key: 加密密钥
    :return: 十六进制字符串
    """
    if len(key) < 16:
        raise RuntimeError("Invalid AES key length (must be 16 bytes)")
    elif len(key) > 16:
        key = key[:16]

    data = data.encode('utf8')
    data = __pkcs7_padding(data, 16)

    cipher = AES.new(key, AES.MODE_ECB)
    result = cipher.encrypt(data)
    return result.encode('hex').upper()


def decrypt(data, key):
    if len(key) < 16:
        raise RuntimeError("Invalid AES key length (must be 16 bytes)")
    elif len(key) > 16:
        key = key[:16]

    data = data.decode('hex')
    cipher = AES.new(key, AES.MODE_ECB)
    result = cipher.decrypt(data)
    data = result.decode('utf8')

    return __depkcs7_padding(data, 16)


if __name__ == '__main__':
    key = "W8p102YW9AZQ117g4t4z241pr6IM9oF49Q3L4pwsuWRE0E7Z04GM1819A217"
    orig_data = "{\"amount\":\"330.0\",\"cardno\":\"\",\"code\":\"1\",\"customernumber\":\"10012430878\",\"externalid\":\"521e95b558e3-456065795ZGT\",\"hmac\":\"d525adaa8c98840642b89b30975690c0\",\"notifytype\":\"SERVER\",\"requestid\":\"yeezgt20150401161206-6949164\"}\n"
    key_for_aes = key[:16]

    print(encrypt(orig_data, key_for_aes))
    this_res = "D8112FF7F6688AA2D6494940DD6EB976DC86AEF0EA46427FA3E8CCAD010F59719B178C38E4377D877F5A733D875CEF12D0D665242E2099FD80A5C319E03D20A88B5EE9493F3EC5CFCDD3E12F6432C08F6C2601CC749E7FC15BC02453C4B2CEEEF562D41FDA1FD5FFFC58DA1AFA7466E920D8B4912A4F622731F50D406A67DB232033BD7710CC5C55BA788B371B1E32199ACAD1ED7707E3DB96DBB3FB9D54FE988AC4A46EE43C486D5979C60A82B132345EE61AB58CF00B61C13D69305BFD09C1F85D05FA3D23836DFD301AF60CDC63B33BC46C6FD21C36C63C750C3F7E2F63A6"
    java_res = "D8112FF7F6688AA2D6494940DD6EB976DC86AEF0EA46427FA3E8CCAD010F59719B178C38E4377D877F5A733D875CEF12D0D665242E2099FD80A5C319E03D20A88B5EE9493F3EC5CFCDD3E12F6432C08F6C2601CC749E7FC15BC02453C4B2CEEEF562D41FDA1FD5FFFC58DA1AFA7466E920D8B4912A4F622731F50D406A67DB232033BD7710CC5C55BA788B371B1E32199ACAD1ED7707E3DB96DBB3FB9D54FE988AC4A46EE43C486D5979C60A82B132345EE61AB58CF00B61C13D69305BFD09C1F85D05FA3D23836DFD301AF60CDC63B320D47D928ED9C9D79E8DDBD520AE9421"
    print("res1:", decrypt(this_res, key_for_aes), "###")
    print("res2:", decrypt(java_res, key_for_aes), "###")

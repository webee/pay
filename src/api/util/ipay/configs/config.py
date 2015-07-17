# -*- coding: utf-8 -*-
from api.util.attr_dict import AttrDict

config = AttrDict(
    root_url='http://localhost:5000',

    platform='lvye.com',
    version='1.0',
    oid_partner='201408071000001546',

    sign_type=AttrDict(
        MD5='MD5',
        RSA='RSA'
    ),

    MD5_key='201408071000001546_test_20140815',

    # 银通公钥
    YT_PUB_KEY="MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCSS/DiwdCf/aZsxxcacDnooGph3d2JOj5GXWi+q3gznZauZjkNP8SKl3J2liP0O6rU/Y/29+IUe+GTMhMOFJuZm1htAtKiu5ekW0GlBMWxf4FPkYlQkPE0FtaoMP3gYfh+OwI+fIRrpW3ySn3mScnc6Z700nU/VYrRkfcSCbSnRwIDAQAB",
    # 商户私钥
    TRADER_PRI_KEY="MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAOilN4tR7HpNYvSBra/DzebemoAiGtGeaxa+qebx/O2YAdUFPI+xTKTX2ETyqSzGfbxXpmSax7tXOdoa3uyaFnhKRGRvLdq1kTSTu7q5s6gTryxVH2m62Py8Pw0sKcuuV0CxtxkrxUzGQN+QSxf+TyNAv5rYi/ayvsDgWdB3cRqbAgMBAAECgYEAj02d/jqTcO6UQspSY484GLsL7luTq4Vqr5L4cyKiSvQ0RLQ6DsUG0g+Gz0muPb9ymf5fp17UIyjioN+ma5WquncHGm6ElIuRv2jYbGOnl9q2cMyNsAZCiSWfR++op+6UZbzpoNDiYzeKbNUz6L1fJjzCt52w/RbkDncJd2mVDRkCQQD/Uz3QnrWfCeWmBbsAZVoM57n01k7hyLWmDMYoKh8vnzKjrWScDkaQ6qGTbPVL3x0EBoxgb/smnT6/A5XyB9bvAkEA6UKhP1KLi/ImaLFUgLvEvmbUrpzY2I1+jgdsoj9Bm4a8K+KROsnNAIvRsKNgJPWd64uuQntUFPKkcyfBV1MXFQJBAJGs3Mf6xYVIEE75VgiTyx0x2VdoLvmDmqBzCVxBLCnvmuToOU8QlhJ4zFdhA1OWqOdzFQSw34rYjMRPN24wKuECQEqpYhVzpWkA9BxUjli6QUo0feT6HUqLV7O8WqBAIQ7X/IkLdzLa/vwqxM6GLLMHzylixz9OXGZsGAkn83GxDdUCQA9+pQOitY0WranUHeZFKWAHZszSjtbe6wDAdiKdXCfig0/rOdxAODCbQrQs7PYy1ed8DuVQlHPwRGtokVGHATU=",

    payment=AttrDict(
        busi_partner=AttrDict(
            virtual_goods='101001',
            physical_goods='109001',
        ),

        default_order_expiration='10080',

        url='https://yintong.com.cn/payment/bankgateway.htm',
        redirect_url='/pay/{uuid}',
        notify_url='/pay/{uuid}/result',
        return_url='http://www.baidu.com'
    ),

    bankcard=AttrDict(
        bin_query_url="https://yintong.com.cn/traderapi/bankcardquery.htm"
    ),

    pay_to_bankcard=AttrDict(
        url="https://yintong.com.cn/traderapi/cardandpay.htm",
        notify_url='/withdraw/{uuid}/result',
    ),

    order=AttrDict(
        url="https://yintong.com.cn/traderapi/orderquery.htm"
    ),

    refund=AttrDict(
        url='https://yintong.com.cn/traderapi/refund.htm',
        notify_url='/refund/{uuid}/result',
    ),
)
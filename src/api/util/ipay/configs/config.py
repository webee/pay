# -*- coding: utf-8 -*-
from api.util.attr_dict import AttrDict

config = AttrDict(
    root_url='http://pay.lvye.com',

    platform='lvye.com',
    version='1.0',
    oid_partner='201507021000395502',

    sign_type=AttrDict(
        MD5='MD5',
        RSA='RSA'
    ),

    MD5_key='x8LmLTRpmXtUcoRuLf7aUa50pwyl73j5kY/d4muoyfU=',

    # 银通公钥
    YT_PUB_KEY='MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCSS/DiwdCf/aZsxxcacDnooGph3d2JOj5GXWi+q3gznZauZjkNP8SKl3J2liP0O6rU/Y/29+IUe+GTMhMOFJuZm1htAtKiu5ekW0GlBMWxf4FPkYlQkPE0FtaoMP3gYfh+OwI+fIRrpW3ySn3mScnc6Z700nU/VYrRkfcSCbSnRwIDAQAB',
    # 商户私钥
    TRADER_PRI_KEY='MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBAKP6LCxwgvI0d+f+JLCJkN/QSsTc3Y/wddThdyQkiY7b2Gz4yN+9eZ1FSZ3lZRZEKkh/7MLK870YU7BFEjVXMYupqC+iU/aaYErNjzzyqATx7O+wPldNeuj80HOqs8VO64wiWB4BhTDoLt24zi9w9UNWQUJYbqZirw185h5EIHThAgMBAAECgYB/AmV4vmUOyYkejoFIpCUs1p8zQIf016HNFB4+RnatyqcmMMUWWCJ8qJBO1sGnr4C4yy1N6/lCvDcGT1m9Kx5Z+cN7UfMIOZOLowG6KafaTikC+rn9oWZuAbv7/8JdWwNkfg1AcKLd7iBZ2UTr5YRgLc+8x6zoDr/lwdBrVUt74QJBALa7+PIfg9rNowXv5wvgffWKXIyH80dRBoRA79DUbryorjC+B4ydD+czV9Aar0iawKjU+oBkNSbQTjxKzgmtcfUCQQDluPWx9UbmclKeVRWigVjcebok/RBCs4FCLOccinoEhmMV5MYwyZhKEPoLXSVjkZpwlTpci7/1hLwJSujqeye9AkA60BMWsof4kzjF/2moi+9eaNLStCrbqDtls5S77LNbaxrtOywo2KA2tHKt2vjRcGVTsYCSdC4bOO4FP7pCqR1FAkEApXUhqcpzBZpD/Xxk98XYHfyi4O9QneoyaFp1H25x0f6FMYi0YwFgacBuiG7PdjayGPKytWOGoCy5TqwgtHp9tQJAANFoYsXHyuzQn0ZBkDENBlIxCNOzmvOJprlUr/dzCr+j5VQptvtbUF3Jlsjob14x9+XUcw5YZZ1CKM+VUA/yxw==',

    payment=AttrDict(
        busi_partner=AttrDict(
            virtual_goods='101001',
            physical_goods='109001',
        ),

        default_order_expiration='10080',

        url='https://yintong.com.cn/payment/bankgateway.htm',
        redirect_url='/pay/{uuid}',
        notify_url='/pay/{uuid}/notify',
        return_url='/pay/{uuid}/result'
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
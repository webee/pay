# -*- coding: utf-8 -*-


class DataBase:
    HOST = 'localhost'
    PORT = 3306
    INSTANCE = 'lvye_pay'
    USERNAME = 'lvye_pay'
    PASSWORD = 'p@55word'


class LianLianPay:
    OID_PARTNER = ''
    PLATFORM = 'lvye.com'
#
# sign_type_md5 = MD5
# sign_type_rsa = RSA
# md5_key = 201408071000001546_test_20140815
# rsa_yt_pub_key = MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCSS/DiwdCf/aZsxxcacDnooGph3d2JOj5GXWi+q3gznZauZjkNP8SKl3J2liP0O6rU/Y/29+IUe+GTMhMOFJuZm1htAtKiu5ekW0GlBMWxf4FPkYlQkPE0FtaoMP3gYfh+OwI+fIRrpW3ySn3mScnc6Z700nU/VYrRkfcSCbSnRwIDAQAB
# rsa_lvye_pri_key = MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAMlGNh/WsyZSYnQcHd9t5qUkhcOhuQmozrAY9DM4+7fhpbJenmYee4chREW4RB3m95+vsz9DqCq61/dIOoLK940/XmhKkuVjfPqHJpoyHJsHcMYy2bXCd2fI++rERdXtYm0Yj2lFbq1aEAckciutyVZcAIHQoZsFwF8l6oS6DmZRAgMBAAECgYAApq1+JN+nfBS9c2nVUzGvzxJvs5I5qcYhY7NGhySpT52NmijBA9A6e60Q3Ku7vQeICLV3uuxMVxZjwmQOEEIEvXqauyYUYTPgqGGcwYXQFVI7raHa0fNMfVWLMHgtTScoKVXRoU3re6HaXB2z5nUR//NE2OLdGCv0ApaJWEJMwQJBAPWoD/Cm/2LpZdfh7oXkCH+JQ9LoSWGpBDEKkTTzIqU9USNHOKjth9vWagsR55aAn2ImG+EPS+wa9xFTVDk/+WUCQQDRv8B/lYZD43KPi8AJuQxUzibDhpzqUrAcu5Xr3KMvcM4Us7QVzXqP7sFc7FJjZSTWgn3mQqJg1X0pqpdkQSB9AkBFs2jKbGe8BeM6rMVDwh7TKPxQhE4F4rHoxEnND0t+PPafnt6pt7O7oYu3Fl5yao5Oh+eTJQbyt/fwN4eHMuqtAkBx/ob+UCNyjhDbFxa9sgaTqJ7EsUpix6HTW9f1IirGQ8ac1bXQC6bKxvXsLLvyLSxCMRV/qUNa4Wxu0roI0KR5AkAZqsY48Uf/XsacJqRgIvwODstC03fgbml890R0LIdhnwAvE4sGnC9LKySRKmEMo8PuDhI0dTzaV0AbvXnsfDfp
#
# url_order_query = https://yintong.com.cn/traderapi/orderquery.htm
# url_pay = https://yintong.com.cn/payment/bankgateway.htm
# url_pay_to_bankcard = https://yintong.com.cn/traderapi/cardandpay.htm
# url_query_bankcard_bin = https://yintong.com.cn/traderapi/bankcardquery.htm
# url_refund = https://yintong.com.cn/traderapi/refund.htm
#
# pay_version = 1.0
# pay_busipartner_virtual_goods = 101001
# pay_busipartner_physical_goods = 109001
# pay_default_order_expiration = 10080
# pay_to_bankcard_version = 1.2
# pay_to_bankcard_result_success = SUCCESS
# pay_to_bankcard_result_waiting = WAITING
# pay_to_bankcard_result_failure = FAILURE
# pay_to_bankcard_result_cancel = CANCEL
# pay_to_bankcard_result_processing = PROCESSING
# order_query_version = 1.1
# order_typedc_pay = 0
# order_typedc_withdraw = 0
# refund_status_applied = 0
# refund_status_processing = 1
# refund_status_success = 2
# refund_status_failed = 3
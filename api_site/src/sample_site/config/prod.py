# coding=utf-8


HOST_URL = "http://prod_sample_pay.lvye.com:8189"


PAYEE = '169658002'


class PayClientConfig:
    MD5_KEY = read_string('conf/md5_key.txt')
    LVYE_PUB_KEY = read_string('conf/lvye_pub_key.txt')
    CHANNEL_PRI_KEY = read_string('conf/channel_pri_key.txt')

    CHANNEL_NAME = 'lvye_pay_test'

    ROOT_URL = "http://pay.lvye.com/api"

# coding=utf-8
from pytoolbox.util import pmc_config
from pytoolbox.util.pmc_config import read_string

ROOT_URL = "http://pay.lvye.com/api/__"


OID_PARTNER = '201507021000395502'
PLATFORM = OID_PARTNER #'lvye.com'

MD5_KEY = read_string('conf/lianlian/md5_key.txt')
YT_PUB_KEY = read_string('conf/lianlian/yt_pub_key.txt')
LVYE_PRI_KEY = read_string('conf/lvye/lvye_pri_key.txt')


class Ftp:
    _ftp = pmc_config.load_yaml('conf/lianlian/ftp.yaml')

    HOSTNAME = _ftp['HOSTNAME']
    PORT = _ftp['PORT']
    USERNAME = _ftp['USERNAME']
    PASSWORD = _ftp['PASSWORD']

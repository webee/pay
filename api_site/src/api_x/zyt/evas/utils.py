# coding=utf-8
from pytoolbox.util import strings
from api_x.config import etc as config
from datetime import datetime

_SN_GEN_LEN = 26
_SN_MAX_LEN = 32


def generate_sn():
    s = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    l = _SN_MAX_LEN - len(s) - len(config.Biz.TX_SN_NUM_SUFFIX)
    return s + strings.gen_rand_str(l, strings.string.ascii_lowercase) + config.Biz.TX_SN_NUM_SUFFIX

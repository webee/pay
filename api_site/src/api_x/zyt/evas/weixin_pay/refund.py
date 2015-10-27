# coding=utf-8
from __future__ import unicode_literals
from pytoolbox.util import strings
from api_x.config import weixin_pay as config
from api_x.zyt.evas.weixin_pay import request, is_success_request, append_md5_sign


def refund(out_refund_no, transaction_id, total_fee, refund_fee,
           refund_fee_type='CNY', device_info='', out_trade_no='', app_config=None):

    app_config = app_config or config.AppConfig()
    params = {
        'appid': app_config.APPID,
        'mch_id': app_config.MCH_ID,
        'device_info': device_info,
        'nonce_str': strings.gen_rand_str(32),
        'transaction_id': transaction_id,
        'out_trade_no': out_trade_no,
        'out_refund_no': out_refund_no,
        'total_fee': total_fee,
        'refund_fee': refund_fee,
        'refund_fee_type': refund_fee_type,
        'op_user_id': app_config.MCH_ID,
    }

    data = request(config.REFUND_URL, params, app_config=app_config, need_cert=True)

    if is_success_request(data, do_raise=True):
        return data


def query_refund():
    pass

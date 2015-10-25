# coding=utf-8
from __future__ import unicode_literals

from flask import url_for
from pytoolbox.util.log import get_logger
from pytoolbox.util import strings
from api_x.config import weixin_pay as config
from .commons import generate_absolute_url
from api_x.zyt.evas import util
from .api_access import request
from .commons import is_success_request


NAME = 'WEIXIN_PAY'
logger = get_logger(__name__)

signers = {}


def prepay(source, trade_type, out_trade_no, total_fee, ip, body, time_start,
           detail='', fee_type='CNY', device_info='WEB',
           attach='', goods_tag='', product_id='', limit_pay='', openid='', app_config=None):
    notify_url = generate_absolute_url(url_for('weixin_pay_entry.pay_notify', source=source))

    time_start = util.utc2gmt8(time_start)
    time_expire = util.time_offset(time_start, offset=config.DEFAULT_ORDER_EXPIRATION_SECONDS)

    app_config = app_config or config.AppConfig()
    params = {
        'appid': app_config.APPID,
        'mch_id': app_config.MCH_ID,
        'device_info': device_info,
        'nonce_str': strings.gen_rand_str(32),
        'body': body[:32],
        'detail': detail[:8192],
        'attach': attach,
        'out_trade_no': out_trade_no,
        'fee_type': fee_type,
        'total_fee': total_fee,
        'spbill_create_ip': ip,
        'time_start': util.datetime_to_str(time_start),
        'time_expire': util.datetime_to_str(time_expire),
        'goods_tag': goods_tag,
        'notify_url': notify_url,
        'trade_type': trade_type,
        'product_id': product_id,
        'limit_pay': limit_pay,  # no_credit--指定不能使用信用卡支付
        'openid': openid,  # trade_type=JSAPI, 此参数必传，用户在商户appid下的唯一标识
    }
    return request(config.UNIFIED_ORDER_URL, params, app=app_config.APP_NAME)

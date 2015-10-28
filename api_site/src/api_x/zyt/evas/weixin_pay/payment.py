# coding=utf-8
from api_x.config import weixin_pay as config
from api_x.utils import times
from api_x.zyt.evas.weixin_pay import request, is_success_request, generate_absolute_url, append_md5_sign
from flask import url_for
from pytoolbox.util import strings


def prepay(source, trade_type, out_trade_no, total_fee, ip, body, time_start,
           detail='', fee_type='CNY', device_info='WEB',
           attach='', goods_tag='', product_id='', limit_pay='', openid='', app_config=None):
    notify_url = generate_absolute_url(url_for('weixin_pay_entry.pay_notify', source=source, app=app_config.APP_NAME))

    time_start = times.utc2gmt8(time_start)
    time_expire = times.time_offset(time_start, offset=config.DEFAULT_ORDER_EXPIRATION_SECONDS)

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
        'time_start': times.datetime_to_str(time_start),
        'time_expire': times.datetime_to_str(time_expire),
        'goods_tag': goods_tag,
        'notify_url': notify_url,
        'trade_type': trade_type,
        'product_id': product_id,
        'limit_pay': limit_pay,  # no_credit--指定不能使用信用卡支付
        'openid': openid,  # trade_type=JSAPI, 此参数必传，用户在商户appid下的唯一标识
    }
    data = request(config.UNIFIED_ORDER_URL, params, app_config=app_config)

    if is_success_request(data, do_raise=True):
        if trade_type == config.TradeType.APP:
            # prepare params
            params = {
                'appid': app_config.APPID,
                'partnerid': app_config.MCH_ID,
                'prepayid': data['prepay_id'],
                'package': 'Sign=WXPay',
                'noncestr': strings.gen_rand_str(32),
                'timestamp': str(int(times.timestamp())),
            }
            params = append_md5_sign(app_config.APP_NAME, params)
            return params
        elif trade_type == config.TradeType.NATIVE:
            return data['code_url']
        return data


def query_order(transaction_id='', out_trade_no='', app_config=None):
    app_config = app_config or config.AppConfig()

    params = {
        'appid': app_config.APPID,
        'mch_id': app_config.MCH_ID,
        'transaction_id': transaction_id,
        'out_trade_no': out_trade_no,
        'nonce_str': strings.gen_rand_str(32),
    }
    data = request(config.QUERY_ORDER_URL, params, app_config=app_config)
    if is_success_request(data, do_raise=True):
        return data

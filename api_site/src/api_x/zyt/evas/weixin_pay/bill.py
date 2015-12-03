# coding=utf-8
from __future__ import unicode_literals

from pytoolbox.util import strings
from datetime import date, datetime
from pytoolbox.util import times
from api_x.config import weixin_pay as config
from .api_access import request
from ..error import DataParsingError


def download_bill(bill_date=None, bill_type=config.BillType.ALL, device_info='', app_config=None):
    from api_access import _parse_data
    app_config = app_config or config.AppConfig()
    if bill_date is None:
        bill_date = times.today()

    params = {
        'appid': app_config.APPID,
        'mch_id': app_config.MCH_ID,
        'device_info': device_info,
        'nonce_str': strings.gen_rand_str(32),
        'bill_date': _date_to_str(bill_date),
        'bill_type': bill_type
    }

    data = request(config.DOWNLOAD_BILL_URL, params, app_config=app_config, ret_raw_data=True, log_resp=False)

    try:
        _ = _parse_data(data)
    except DataParsingError as _:
        pass

    lines = data.splitlines()
    header = lines[0]
    names = header.split(',')
    res = []
    for line in lines[1:-2]:
        values = line.lstrip('`').split(',`')
        res.append(values)
    stat_names = lines[-2].split(',')
    state_values = lines[-1].lstrip('`').split(',`')
    return names, res, stat_names, state_values


def _date_to_str(dt):
    if isinstance(dt, (date, datetime)):
        return dt.strftime('%Y%m%d')
    return dt


# coding=utf-8
from __future__ import unicode_literals
from functools import wraps
from flask import request, redirect, url_for
import urlparse
from pytoolbox.util.log import get_logger
from pub_site.constant import RequestClientType
from pub_site.utils import req


logger = get_logger(__name__)


def pay_limit_referrer(netlocs):
    def do_limit(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                sn = request.view_args.get('sn')
                vas_name = request.view_args.get('vas_name')
                client_type = req.client_type()
                referrer = request.referrer
                logger.info("client type: [{0}], referrer: [{1}]".format(client_type, referrer))
                if client_type != RequestClientType.WEB and referrer is None:
                    if vas_name == 'LIANLIAN_PAY':
                        # FIXME: 连连支付h5无法返回的问题
                        # 此为连连返回, 则直接去收银台
                        return redirect(url_for('checkout_entry.checkout', sn=sn, activated_vas='LIANLIAN_PAY'))
                parts = urlparse.urlparse(referrer)
                if parts.netloc in netlocs:
                    return f(*args, **kwargs)
            except Exception as e:
                logger.exception(e)
            return "非法请求"
        return wrapper
    return do_limit

# -*- coding: utf-8 -*-
from datetime import datetime
from urlparse import urljoin

from ..uuid import encode_uuid
from pytoolbox.conf import config


def datetime_to_str(timestamp):
    return timestamp.strftime('%Y%m%d%H%M%S')


def now_to_str():
    return datetime_to_str(datetime.now())


def generate_url(relative_url, id, **kwargs):
    params = {'uuid': encode_uuid(id)}
    params.update(kwargs)
    relative_url = relative_url.format(**params)
    root_url = config.get('hosts', 'api_gateway')
    return urljoin(root_url, relative_url)

# coding=utf-8
from __future__ import unicode_literals

import urllib
import urlparse


def build_url(base_url, *args, **kwargs):
    parts = urlparse.urlparse(base_url)

    target_params = urlparse.parse_qs(parts.query, keep_blank_values=True)
    added_params = [params for params in args]
    added_params.append(kwargs)

    for params in added_params:
        for k, v in params.items():
            target_params.setdefault(k, []).append(v)

    parts = list(parts)
    # [0]scheme, [1]netloc, [2]path, [3]params, [4]query, [5]fragment
    parts[4] = urllib.urlencode(target_params, doseq=True)

    return urlparse.urlunparse(parts)

# coding=utf-8
from __future__ import unicode_literals

from api_x.config import lianlian_pay


def generate_absolute_url(path):
    return lianlian_pay.ROOT_URL + path

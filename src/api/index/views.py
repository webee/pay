# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from flask import redirect

from . import index_mod as mod


@mod.route('/')
def index():
    return _redirect_to_official_host


def _redirect_to_official_host():
    return redirect('http://huodong.lvye.com')

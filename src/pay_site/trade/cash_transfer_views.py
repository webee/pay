# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

import logging
from datetime import datetime
from flask import request, redirect, url_for, jsonify
from tools.dbi import from_db
from tools.dbi import transactional
from tools.mylog import get_logger
from . import trade_mod as mod
import zgt.service as zgt


logger = get_logger(__name__)


@mod.route('/cash_transfer/', methods=['GET', 'POST'])
def cash_transfer():
    """提现接口
    :return:
    """
    # TODO: 加密接口数据
    data = request.args
    if request.method == 'POST':
        data = request.form

    pass

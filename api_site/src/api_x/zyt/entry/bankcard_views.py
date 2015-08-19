# coding=utf-8
from __future__ import unicode_literals

from . import biz_entry_mod as mod
from api_x.utils import response
from tools.mylog import get_logger
from api_x.zyt.biz import bankcard

logger = get_logger(__name__)


@mod.route('/bankcard/<card_no>/bin', methods=['GET'])
def query_bin(card_no):
    try:
        card_bin = bankcard.query_bin(card_no)
        return response.success(**(card_bin.to_dict()))
    except Exception as e:
        logger.exception(e)
        return response.bad_request(msg=e.message)

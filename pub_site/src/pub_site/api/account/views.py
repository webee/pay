# coding=utf-8
from __future__ import unicode_literals
from flask.ext.login import current_user
from . import account_mod as mod
from pub_site import pay_client
from ..utils import login_required
from .. import response


@mod.route('/balance/', methods=['GET'])
@login_required
def balance():
    user_id = current_user.user_id
    result = pay_client.app_query_user_balance(user_id)
    return response.success(result)

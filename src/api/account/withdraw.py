# coding=utf-8
from __future__ import unicode_literals
from api.attr_dict import AttrDict
from api.base_config import lianlian_base_config
from datetime import datetime
import uuid
from tools.dbi import from_db, transactional


@transactional
def create_withdraw_order(account_id, bandcard_id, amount):
    """ 新建提现订单
    :param account_id: 提现账户id
    :param bandcard_id: 银行卡id
    :param amount: 提现金额
    :return:
    """
    order_id = _generate_transaction_id(account_id)
    fields = {
        'id': order_id,
        'account_id': account_id,
        'bankcard_id': bandcard_id,
        'amount': amount,
        'created_on': datetime.now(),
    }

    from_db().insert('withdraw', **fields)

    return order_id


def _generate_transaction_id(account_id):
    return datetime.now().strftime("%Y%m%d%H%M%S%f") + '%0.7d' % account_id + uuid.uuid4().hex[:5]

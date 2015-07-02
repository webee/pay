# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from pay_op_site.domain import *
import logging, httplib

log = logging.getLogger(__name__)

mod = Blueprint('trade', __name__, template_folder='', static_folder='static')


@mod.route('/trade/pay', methods=['POST'])
def pay_action():
    data = request.form
    source_channel = data.get('source_channel', None)
    source_order_id = data.get('source_order_id', None)
    source_order_name = data.get('source_order_name', None)
    payer = data.get('payer', None)
    amount = float(data.get('amount', -1))
    if source_channel is None or source_order_id is None or source_order_name is None or amount <= 0:
        abort(httplib.BAD_REQUEST)
    trades = from_db().list('select * from pay_trades')
    trade_id = create_trade_record(source_channel, source_order_id, source_order_name, amount, payer, trade_type=1)
    print(trade_id)

    print(trades)
    return redirect(get_payment_agent_url())


@transactional
def create_trade_record(source_channel, source_order_id, source_order_name, amount, payer, trade_type):
    return from_db().insert('pay_trades', returns_id=True,
                            source_channel=source_channel,
                            source_order_id=source_order_id,
                            source_order_name=source_order_name,
                            amount=amount,
                            payer=payer,
                            trade_type=trade_type
                            )



def get_payment_agent_url():
    return 'http://www.baidu.com'

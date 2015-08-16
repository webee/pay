# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import Blueprint, request
from api_x.zyt.entry.business.business_models import TransferRecord


mod = Blueprint('main', __name__)


@mod.route('/transfer', methods=['POST'])
def transfer():
    data = request.values
    from_user_id = data['from_user']
    to_user_id = data['to_user']
    amount = data['amount']

    # check balance.

    # transfer

    transfer_record = TransferRecord(from_user_id=from_user_id, to_user_id=to_user_id, amount=amount)



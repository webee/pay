# coding=utf-8
from __future__ import unicode_literals

from pytoolbox.util.dbs import transactional
from pub_site.models import PayToLvyeRecord
from pub_site.commons import generate_order_id
from pub_site import db


@transactional
def add_pay_to_lvye_record(user_id, amount, name, comment):
    order_id = generate_order_id(user_id)

    pay_to_lvye_record = PayToLvyeRecord(order_id=order_id, user_id=user_id, amount=amount, name=name, comment=comment)
    db.session.add(pay_to_lvye_record)

    return pay_to_lvye_record


@transactional
def update_record_state(sn, user_id, new_state):
    record = PayToLvyeRecord.query.filter_by(sn=sn, user_id=user_id).first()
    if record is None:
        return

    record.state = new_state
    db.session.add(record)

    return record

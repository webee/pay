# coding=utf-8
from __future__ import unicode_literals

from pub_site import db
from pub_site.models import PreferredCard, WithdrawRecord
from pytoolbox.util.dbs import transactional


@transactional
def update_user_preferred_card(user_id, bankcard_id):
    preferred_card = PreferredCard.query.filter_by(user_id=user_id).first()
    if preferred_card is None:
        preferred_card = PreferredCard()
    preferred_card.user_id = user_id
    preferred_card.bankcard_id = bankcard_id

    db.session.add(preferred_card)


def get_preferred_card_id(user_id):
    preferred_card = PreferredCard.query.filter_by(user_id=user_id).first()
    return preferred_card.bankcard_id


@transactional
def add_withdraw_record(sn, user_id, bankcard_id, phone_no, amount, actual_amount, fee):
    withdraw_record = WithdrawRecord(sn=sn, user_id=user_id, bankcard_id=bankcard_id, phone_no=phone_no,
                                     amount=amount, actual_amount=actual_amount, fee=fee)
    db.session.add(withdraw_record)


@transactional
def get_withdraw_record(sn, user_id):
    return WithdrawRecord.query.filter_by(sn=sn, user_id=user_id).first()

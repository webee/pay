# coding=utf-8
from __future__ import unicode_literals

from pub_site import db
from pub_site.models import PreferredCard, WithdrawRecord
from pytoolbox.util.dbs import transactional
from pub_site.constant import WithdrawState


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
    if preferred_card:
        return preferred_card.bankcard_id


@transactional
def add_withdraw_record(sn, user_id, bankcard_id, phone_no, amount, actual_amount, fee):
    withdraw_record = WithdrawRecord(sn=sn, user_id=user_id, bankcard_id=bankcard_id,
                                     phone_no=phone_no, state=WithdrawState.REQUESTED,
                                     amount=amount, actual_amount=actual_amount, fee=fee)
    db.session.add(withdraw_record)

    return withdraw_record


@transactional
def update_withdraw_state(sn, user_id, new_state):
    withdraw_record = WithdrawRecord.query.filter_by(sn=sn, user_id=user_id).first()
    if withdraw_record is None:
        return

    withdraw_record.state = new_state
    db.session.add(withdraw_record)

    return withdraw_record


def get_withdraw_record(sn, user_id):
    return WithdrawRecord.query.filter_by(sn=sn, user_id=user_id).first()


def get_requested_withdraw_record_before(t):
    return WithdrawRecord.query.filter(WithdrawRecord.created_on < t).all()

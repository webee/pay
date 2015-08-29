# coding=utf-8
from __future__ import unicode_literals

from pub_site import db
from pub_site.models import PreferredCard
from pytoolbox.util.dbs import transactional


@transactional
def update_user_preferred_card(user_id, bankcard_id):
    preferred_card = PreferredCard.query.filter_by(user_id=user_id).first()
    if preferred_card is None:
        preferred_card = PreferredCard()
    preferred_card.user_id = user_id
    preferred_card.bankcard_id = bankcard_id

    db.session.add(preferred_card)

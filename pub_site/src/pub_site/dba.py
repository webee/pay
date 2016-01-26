# coding=utf-8
from __future__ import unicode_literals
from pub_site import db
from pytoolbox.util.dbs import transactional
from .models import LvyeAccount
from pytoolbox.util.log import get_logger

logger = get_logger(__name__)


def is_username_exists(username):
    return LvyeAccount.query.filter_by(username=username).count() > 0


@transactional
def create_or_update_lvye_account(username, user_id):
    lvye_account = LvyeAccount.query.filter_by(username=username).first()
    if lvye_account is None:
        lvye_account = LvyeAccount(username=username, user_id=user_id)
    if lvye_account.user_id != user_id:
        if LvyeAccount.query.filter_by(user_id=user_id).count() > 0:
            # something error.
            logger.warn('duplicated lvye_account: [{0}], [{1}]'.format(user_id, username))
        else:
            lvye_account.user_id = user_id
    db.session.add(lvye_account)

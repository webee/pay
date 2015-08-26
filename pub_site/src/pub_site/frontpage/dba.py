# coding=utf-8
from __future__ import unicode_literals

from pytoolbox.util.dbs import transactional
from pub_site import db
from pub_site.models import LeaderApplication


@transactional
def add_leader_application(user_domain_name, user_id, user_name):
    leader_application = LeaderApplication.query.filter_by(user_domain_name=user_domain_name, user_id=user_id).first()
    if leader_application is None:
        leader_application = LeaderApplication(user_domain_name=user_domain_name, user_id=user_id, user_name=user_name)

    db.session.add(leader_application)

    return leader_application.id

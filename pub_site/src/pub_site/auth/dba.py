# coding=utf-8
from __future__ import unicode_literals
from pub_site import db
from pytoolbox.util.dbs import transactional
from .models import DomainUser
from pub_site.models import LeaderApplication


def is_leader_applied(user_id):
    return LeaderApplication.query.filter_by(user_id=user_id).count() > 0


@transactional
def add_domain_user(user_domain_name, username, phone, password):
    du = DomainUser(user_domain_name=user_domain_name, username=username, phone=phone, password=password)
    db.session.add(du)

    return du

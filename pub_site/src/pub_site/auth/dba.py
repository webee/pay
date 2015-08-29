# coding=utf-8
from __future__ import unicode_literals
from pub_site.models import LeaderApplication


def is_leader_applied(user_id):
    return LeaderApplication.query.filter_by(user_id=user_id).count() > 0

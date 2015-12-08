# coding=utf-8
from __future__ import unicode_literals

from collections import namedtuple
from api_x.zyt.biz.models import UserRole


RoleUser = namedtuple('RoleUser', ['user_id', 'role'])


def from_user(user_id):
    return RoleUser(user_id, UserRole.FROM)


def to_user(user_id):
    return RoleUser(user_id, UserRole.TO)


def guaranteed_by(user_id):
    return RoleUser(user_id, UserRole.GUARANTOR)


def tx_from_user(user_id):
    return RoleUser(user_id, UserRole.TX_FROM)


def tx_to_user(user_id):
    return RoleUser(user_id, UserRole.TX_TO)

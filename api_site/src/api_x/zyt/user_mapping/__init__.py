# coding=utf-8
from api_x import db
from api_x.dbs import transactional
from api_x.zyt.vas.user import create_user
from .models import UserDomain, Channel, UserMap


@transactional
def create_user_domain(name):
    user_domain = UserDomain(name=name)
    db.session.add(user_domain)

    return user_domain


def get_user_domain(id):
    return UserDomain.query.get(id)


@transactional
def create_channel(user_domain_id, name):
    channel = Channel(user_domain_id=user_domain_id, name=name)
    db.session.add(channel)

    return channel


def get_system_account_user_id(user_id):
    from api_x.constant import SYSTEM_USER_DOMAIN_NAME
    user_domain = UserDomain.query.filter_by(name=SYSTEM_USER_DOMAIN_NAME).first()
    user_map = UserMap.query.filter_by(user_domain_id=user_domain.id, user_id=user_id).one()
    return user_map.account_user_id


def get_account_user_id_by_by_domain_info(user_domain_id, user_id):
    user_map = UserMap.query.filter_by(user_domain_id=user_domain_id, user_id=user_id).one()
    return user_map.account_user_id


@transactional
def find_or_create_account_user(user_domain_id, user_id):
    user_domain = get_user_domain(user_domain_id)
    user_map = UserMap.query.filter_by(user_domain_id=user_domain_id, user_id=user_id).first()
    if user_map is None:
        account_user = create_user()
        user_map = UserMap(user_domain_id=user_domain_id, user_id=user_id, account_user_id=account_user.id,
                           info=user_domain.name)
        db.session.add(user_map)

    return user_map.account_user_id


def get_channel_info(channel_id):
    return Channel.query.get(channel_id)


@transactional
def find_or_create_account_user_by_channel_info(channel_id, user_id):
    channel_info = get_channel_info(channel_id)

    return find_or_create_account_user(channel_info.user_domain_id, user_id)

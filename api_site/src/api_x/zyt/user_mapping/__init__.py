# coding=utf-8
from api_x import db
from api_x.dbs import transactional
from api_x.zyt.vas.user import create_user
from .models import UserDomain, Channel, UserMapping


@transactional
def create_user_domain(name, desc):
    user_domain = UserDomain(name=name, desc=desc)
    db.session.add(user_domain)

    return user_domain


def get_user_domain(id):
    return UserDomain.query.get(id)


def get_user_domain_by_name(name):
    return UserDomain.query.filter_by(name=name).first()


@transactional
def create_channel(user_domain_id, name, desc):
    channel = Channel(user_domain_id=user_domain_id, name=name, desc=desc)
    db.session.add(channel)

    return channel


def get_system_account_user_id(user_id):
    from api_x.constant import DefaultUserDomain
    user_domain = UserDomain.query.filter_by(name=DefaultUserDomain.SYSTEM_USER_DOMAIN_NAME).first()
    user_map = UserMapping.query.filter_by(user_domain_id=user_domain.id, user_id=user_id).one()
    return user_map.account_user_id


def get_lvye_corp_account_user_id(user_id):
    from api_x.constant import DefaultUserDomain
    user_domain = UserDomain.query.filter_by(name=DefaultUserDomain.LVYE_CORP_DOMAIN_NAME).first()
    user_map = UserMapping.query.filter_by(user_domain_id=user_domain.id, user_id=user_id).one()
    return user_map.account_user_id


def get_user_map(user_domain_id, user_id):
    user_map = UserMapping.query.filter_by(user_domain_id=user_domain_id, user_id=user_id).first()
    return user_map


@transactional
def create_account_user(user_domain_id, user_id, desc=None):
    user_domain = get_user_domain(user_domain_id)
    if user_domain is not None:
        account_user = create_user()
        user_map = UserMapping(user_domain_id=user_domain_id, user_id=user_id, account_user_id=account_user.id,
                               desc=desc or user_domain.desc)
        db.session.add(user_map)

        return account_user.id


@transactional
def get_or_create_account_user(user_domain_id, user_id):
    user_map = UserMapping.query.filter_by(user_domain_id=user_domain_id, user_id=user_id).first()
    if user_map is None:
        return create_account_user(user_domain_id, user_id)

    return user_map.account_user_id


def get_channel(id):
    return Channel.query.get(id)


def get_channel_by_name(name):
    return Channel.query.filter_by(name=name).first()


@transactional
def find_or_create_account_user_by_channel_info(channel_id, user_id):
    channel = get_channel(channel_id)

    return get_or_create_account_user(channel.user_domain_id, user_id)

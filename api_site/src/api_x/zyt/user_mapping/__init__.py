# coding=utf-8
from api_x import db
from api_x.config import etc as config
from api_x.zyt.vas.user import create_user
from .models import UserDomain, Channel, UserMapping, ApiEntry, ChannelPermission
from pytoolbox.util.dbs import transactional
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


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
def create_channel(user_domain_name, name, desc, md5_key='', public_key=''):
    # NOTE: 为方便，非线上创建channel自动加上统一的md5_key和public_key
    if config.__env_name__ != 'prod':
        md5_key = md5_key or config.TEST_MD5_KEY
        public_key = public_key or config.TEST_CHANNEL_PUB_KEY
    user_domain = get_user_domain_by_name(user_domain_name)
    channel = Channel(user_domain_id=user_domain.id, name=name, desc=desc, md5_key=md5_key, public_key=public_key)
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


def get_user_map_by_domain_name_and_user_id(user_domain_name, user_id):
    user_domain = UserDomain.query.filter_by(name=user_domain_name).first()

    return user_domain.user_maps.filter_by(user_id=user_id).first()


def get_user_map_by_account_user_id(account_user_id):
    user_map = UserMapping.query.filter_by(account_user_id=account_user_id).first()
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
def create_domain_account_user(user_domain_name, user_id, desc=None):
    user_domain = get_user_domain_by_name(user_domain_name)
    return create_account_user(user_domain.id, user_id, desc)


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


@transactional
def add_perm_to_channel(channel_name, api_entry_name):
    channel = get_channel_by_name(channel_name)
    if channel.has_entry_perm(api_entry_name):
        return

    api_entry = ApiEntry.query.filter_by(name=api_entry_name).first()

    channel_perm = ChannelPermission(channel_id=channel.id, api_entry_id=api_entry.id)

    db.session.add(channel_perm)


@transactional
def update_api_entries():
    from api_x.utils.entry_auth import get_api_entry_name_list

    entry_names = get_api_entry_name_list()

    # add news.
    for name in entry_names:
        api_entry = ApiEntry.query.filter_by(name=name).first()
        if api_entry is None:
            api_entry = ApiEntry(name=name)
        db.session.add(api_entry)

    # delete discards.
    for api_entry in ApiEntry.query.all():
        if api_entry.name not in entry_names:
            for channel_perm in api_entry.channel_perms.all():
                # delete exists perm.
                db.session.delete(channel_perm)
            db.session.delete(api_entry)


@transactional
def set_user_is_opened(user_domain_name, user_id, status=True):
    """status=True: 开通, False: 关闭"""
    user_map = get_user_map_by_domain_name_and_user_id(user_domain_name, user_id)
    if user_map is None:
        create_domain_account_user(user_domain_name, user_id)
        user_map = get_user_map_by_domain_name_and_user_id(user_domain_name, user_id)

    user_map.is_opened = status
    db.session.add(user_map)

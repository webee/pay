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
    from api_x.config import weixin_pay
    if config.__env_name__ != 'prod':
        md5_key = md5_key or config.TEST_MD5_KEY
        public_key = public_key or config.TEST_CHANNEL_PUB_KEY
    user_domain = get_user_domain_by_name(user_domain_name)
    channel = Channel(user_domain_id=user_domain.id, name=name, desc=desc, md5_key=md5_key, public_key=public_key)
    channel.wx_main = weixin_pay.WX_MAIN
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
def create_domain_account_user(user_domain, user_id, desc=None):
    account_user = create_user()
    user_map = UserMapping(user_domain_id=user_domain.id, user_id=user_id, account_user_id=account_user.id,
                           desc=desc or user_domain.desc)
    db.session.add(user_map)

    return account_user.id


def create_account_user(user_domain_id, user_id, desc=None):
    user_domain = get_user_domain(user_domain_id)
    if user_domain is not None:
        return create_domain_account_user(user_domain, user_id, desc)


@transactional
def create_account_user_by_domain_name(user_domain_name, user_id, desc=None):
    user_domain = get_user_domain_by_name(user_domain_name)
    if user_domain is not None:
        return create_domain_account_user(user_domain, user_id, desc)


def get_channel(id):
    return Channel.query.get(id)


def get_channel_by_name(name):
    return Channel.query.filter_by(name=name).first()


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
    from api_x.utils.entry_auth import get_super_sub_entries

    super_sub_entries = get_super_sub_entries()
    entry_names = []

    def add_entry(e, s_id=None):
        entry_names.append(e)
        _e = ApiEntry.query.filter_by(name=e).first()
        if _e is None:
            _e = ApiEntry(name=e, super_id=s_id)
            db.session.add(_e)
            db.session.flush()
        return _e.id

    for s, es in super_sub_entries.iteritems():
        _e_id = None
        if s is not None:
            _e_id = add_entry(s)
        for _s in es:
            add_entry(_s, _e_id)

    _delete_discards_entries(entry_names)


def _delete_discards_entries(current_entries):
    deleted = []

    def delete_entry(entry):
        for ae in entry.subs.all():
            for channel_perm in entry.channel_perms.all():
                # delete exists perm.
                db.session.delete(channel_perm)
            delete_entry(ae)
        db.session.delete(entry)
        deleted.append(entry.name)

    # delete discards.
    for api_entry in ApiEntry.query.all():
        if api_entry.name not in current_entries and api_entry.name not in deleted:
            delete_entry(api_entry)


@transactional
def set_user_is_opened(user_domain_name, user_id, status=True):
    """status=True: 开通, False: 关闭"""
    user_map = get_user_map_by_domain_name_and_user_id(user_domain_name, user_id)
    if user_map is None:
        create_account_user_by_domain_name(user_domain_name, user_id)
        user_map = get_user_map_by_domain_name_and_user_id(user_domain_name, user_id)

    user_map.is_opened = status
    db.session.add(user_map)

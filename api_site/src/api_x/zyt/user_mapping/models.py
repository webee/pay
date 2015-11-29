# coding=utf-8
from __future__ import unicode_literals
from api_x import db
from datetime import datetime
from ..vas import user
from pytoolbox.util.dbs import transactional


class UserDomain(db.Model):
    __tablename__ = 'user_domain'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(32), nullable=False, unique=True)
    desc = db.Column(db.VARCHAR(64), nullable=False, default='')

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @transactional
    def get_user_map(self, user_id):
        return self.user_maps.filter_by(user_id=user_id).first()

    @transactional
    def get_add_user_map(self, user_id, desc=None):
        user_map = self.user_maps.filter_by(user_id=user_id).first()
        if user_map is None:
            account_user = user.create_user()
            user_map = UserMapping(user_domain_id=self.id, user_id=user_id, account_user_id=account_user.id,
                                   desc=desc or self.desc)
            db.session.add(user_map)
        return user_map

    def __repr__(self):
        return 'UserDomain<%r>' % (self.name,)


class UserMapping(db.Model):
    __tablename__ = 'user_mapping'

    id = db.Column(db.Integer, primary_key=True)
    user_domain_id = db.Column(db.Integer, db.ForeignKey('user_domain.id'), nullable=False)
    user_domain = db.relationship('UserDomain', backref=db.backref('user_maps', lazy='dynamic'))
    user_id = db.Column(db.VARCHAR(32), nullable=False)
    account_user_id = db.Column(db.Integer, nullable=False, unique=True)

    # 是否已开通
    is_opened = db.Column(db.BOOLEAN, nullable=False, default=False)

    desc = db.Column(db.VARCHAR(64), default='')

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    opened_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # index
    # 目前<user_domain_id, user_id>唯一确定一个账号用户，之后可能对应多个
    __table_args__ = (db.UniqueConstraint('user_domain_id', 'user_id', name='domain_user_id_uniq_idx'),)

    def __repr__(self):
        return 'UserMapping<%r: %r, %r>' % (self.user_id, self.account_user_id, self.desc)


class Channel(db.Model):
    __tablename__ = 'channel'

    id = db.Column(db.Integer, primary_key=True)
    user_domain_id = db.Column(db.Integer, db.ForeignKey('user_domain.id'), nullable=False)
    user_domain = db.relationship('UserDomain', backref=db.backref('channels', lazy='dynamic'), lazy='joined')

    # channel name唯一对应一个user_domain
    name = db.Column(db.VARCHAR(32), nullable=False, unique=True)

    md5_key = db.Column(db.VARCHAR(64))
    public_key = db.Column(db.TEXT)
    desc = db.Column(db.VARCHAR(64), nullable=False, default='')

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # enable zyt pay
    zyt_pay_enabled = db.Column(db.BOOLEAN, nullable=False, default=False)

    def __init__(self, *args, **kwargs):
        super(Channel, self).__init__(*args, **kwargs)

    def has_entry_perm(self, api_entry_path, level=0):
        _, api_entry_trie = ApiEntry.load_trie()
        api_entry = api_entry_trie[api_entry_path]
        id_path = api_entry.id_path
        if level:
            id_path = id_path[-level:]

        return self.perms.filter(ChannelPermission.api_entry_id.in_(id_path)).count() > 0

    def get_user_map(self, user_id):
        return self.user_domain.user_maps.filter_by(user_id=user_id).first()

    def get_add_user_map(self, user_id):
        return self.user_domain.get_add_user_map(user_id)

    def __repr__(self):
        return 'Channel<%r>' % (self.name,)


class ApiEntry(db.Model):
    __tablename__ = 'api_entry'

    id = db.Column(db.Integer, primary_key=True)
    super_id = db.Column(db.Integer, db.ForeignKey('api_entry.id'), nullable=True, default=None)
    super = db.relationship('ApiEntry', remote_side=id, backref=db.backref('subs', lazy='dynamic'), lazy='joined')

    name = db.Column(db.VARCHAR(64), nullable=False, index=True)
    value = db.Column(db.VARCHAR(256), nullable=True)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('super_id', 'name', name='super_id_name_uniq_idx'),)

    @staticmethod
    def load_trie():
        from api_x.utils import ds
        trie = ds.Trie()

        api_entries = ApiEntry.query.all()
        for api_entry in api_entries:
            if api_entry.value is not None:
                trie.put(api_entry.path, api_entry)
        return api_entries, trie

    @property
    def path(self):
        s, path = self, tuple()
        while s is not None:
            path = (s.name,) + path
            s = s.super
        return path

    @property
    def id_path(self):
        s, path = self, tuple()
        while s is not None:
            path = (s.id,) + path
            s = s.super
        return path

    def __repr__(self):
        return 'ApiEntry<%r>' % (self.path, )


class ChannelPermission(db.Model):
    __tablename__ = 'channel_permission'

    id = db.Column(db.Integer, primary_key=True)

    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    channel = db.relationship('Channel', backref=db.backref('perms', lazy='dynamic'), lazy='joined')

    api_entry_id = db.Column(db.Integer, db.ForeignKey('api_entry.id'), nullable=False)
    api_entry = db.relationship('ApiEntry', backref=db.backref('channel_perms', lazy='dynamic'), lazy='joined')

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('channel_id', 'api_entry_id', name='channel_api_entry_uniq_idx'),)

    def __repr__(self):
        return 'ChannelPermission<%r->%r>' % (self.channel.name, self.api_entry.path)

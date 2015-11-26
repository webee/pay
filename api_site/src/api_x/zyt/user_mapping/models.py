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

    def has_entry_perm(self, api_entry_name, level=1):
        from sqlalchemy.orm import lazyload

        has_perm = self.perms.options(lazyload('api_entry')).outerjoin(ApiEntry).filter(ApiEntry.name == api_entry_name).count() > 0
        if has_perm or level >= 2:
            return has_perm

        e = ApiEntry.query.filter_by(name=api_entry_name).first()
        if e is None or e.super is None:
            return False
        e = e.super
        return self.has_entry_perm(e.name, level=level+1)

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

    name = db.Column(db.VARCHAR(64), nullable=False, unique=True)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class ChannelPermission(db.Model):
    __tablename__ = 'channel_permission'

    id = db.Column(db.Integer, primary_key=True)

    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    channel = db.relationship('Channel', backref=db.backref('perms', lazy='dynamic'), lazy='joined')

    api_entry_id = db.Column(db.Integer, db.ForeignKey('api_entry.id'), nullable=False)
    api_entry = db.relationship('ApiEntry', backref=db.backref('channel_perms', lazy='dynamic'), lazy='joined')

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('channel_id', 'api_entry_id', name='channel_api_entry_uniq_idx'),)

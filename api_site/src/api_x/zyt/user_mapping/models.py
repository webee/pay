# coding=utf-8
from __future__ import unicode_literals
from api_x import db
from datetime import datetime


class UserDomain(db.Model):
    __tablename__ = 'user_domain'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(32), nullable=False, unique=True)
    desc = db.Column(db.VARCHAR(64), nullable=False, default='')

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return 'UserDomain<%r>' % (self.name,)


class Channel(db.Model):
    __tablename__ = 'channel'

    id = db.Column(db.BigInteger, primary_key=True)
    user_domain_id = db.Column(db.Integer, db.ForeignKey('user_domain.id'), nullable=False)
    user_domain = db.relationship('UserDomain', backref=db.backref('channels', lazy='dynamic'))

    name = db.Column(db.VARCHAR(32), nullable=False, unique=True)
    desc = db.Column(db.VARCHAR(64), nullable=False, default='')

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return 'Channel<%r>' % (self.name,)


class UserMapping(db.Model):
    __tablename__ = 'user_mapping'

    id = db.Column(db.BigInteger, primary_key=True)
    user_domain_id = db.Column(db.Integer, db.ForeignKey('user_domain.id'), nullable=False)
    user_domain = db.relationship('UserDomain', backref=db.backref('user_maps', lazy='dynamic'))
    user_id = db.Column(db.VARCHAR(32), nullable=False)
    account_user_id = db.Column(db.Integer, nullable=False, unique=True)
    desc = db.Column(db.VARCHAR(64), default='')

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # index
    __table_args__ = (db.UniqueConstraint('user_domain_id', 'user_id', name='domain_user_id_uniq_idx'),)

    def __repr__(self):
        return 'UserMapping<%r, %r>' % (self.user_id, self.account_user_id)

# coding=utf-8
from __future__ import unicode_literals
from api_x import db
from datetime import datetime


class UserDomain(db.Model):
    __tablename__ = 'user_domain'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(32), nullable=False, unique=True)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Channel(db.Model):
    __tablename__ = 'channel'

    id = db.Column(db.BigInteger, primary_key=True)
    user_domain_id = db.Column(db.Integer, db.ForeignKey('user_domain.id'), nullable=False)
    user_domain = db.relationship('UserDomain', backref=db.backref('channels', lazy='dynamic'))

    name = db.Column(db.VARCHAR(32), nullable=False, unique=True)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class UserMapping(db.Model):
    __tablename__ = 'user_mapping'

    id = db.Column(db.BigInteger, primary_key=True)
    user_domain_id = db.Column(db.Integer, db.ForeignKey('user_domain.id'), nullable=False)
    user_domain = db.relationship('UserDomain', backref=db.backref('user_maps', lazy='dynamic'))

    user_id = db.Column(db.VARCHAR(32), nullable=False)
    info = db.Column(db.VARCHAR(32), default='')

    account_user_id = db.Column(db.Integer, nullable=False)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # index
    __table_args__ = (db.UniqueConstraint('user_domain_id', 'user_id', name='domain_user_id_uniq_idx'),)

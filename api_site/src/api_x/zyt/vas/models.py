# coding=utf-8
from __future__ import unicode_literals, print_function

from api_x import db
from datetime import datetime


class LiabilityType:
    TOTAL = 'TOTAL'
    AVAILABLE = 'AVAILABLE'
    FROZEN = 'FROZEN'


class EventType:
    TRANSFER_IN = 'TRANSFER_IN'
    TRANSFER_OUT = 'TRANSFER_OUT'
    FREEZE = 'FREEZE'
    UNFREEZE = 'UNFREEZE'
    TRANSFER_IN_FROZEN = 'TRANSFER_IN_FROZEN'
    TRANSFER_OUT_FROZEN = 'TRANSFER_OUT_FROZEN'


class AccountUser(db.Model):
    __tablename__ = 'account_user'

    id = db.Column(db.Integer, primary_key=True)

    is_locked = db.Column(db.Boolean, nullable=False, default=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<AccountUser %r>' % (self.id,)


class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.BigInteger, primary_key=True)
    tx_sn = db.Column(db.CHAR(32), nullable=False)
    vas_name = db.Column(db.VARCHAR(32), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('account_user.id'), nullable=False)
    user = db.relationship('AccountUser', backref=db.backref('events', lazy='dynamic'))

    type = db.Column(db.Enum(EventType.TRANSFER_IN, EventType.TRANSFER_OUT,
                             EventType.FREEZE, EventType.UNFREEZE,
                             EventType.TRANSFER_IN_FROZEN, EventType.TRANSFER_OUT_FROZEN), nullable=False)

    amount = db.Column(db.Numeric(16, 2), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Event %r, %r, %r>' % (self.id, self.user_id, self.amount)


class SystemAssetAccountItem(db.Model):
    __tablename__ = 'system_asset_account_item'

    id = db.Column(db.BigInteger, primary_key=True)
    vas_name = db.Column(db.VARCHAR(32), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('account_user.id'), nullable=False)
    user = db.relationship('AccountUser', backref=db.backref('asset_account_items', lazy='dynamic'))

    event_id = db.Column(db.BigInteger, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref=db.backref('asset_account_items', lazy='dynamic'))

    side = db.Column(db.Enum('DEBIT', 'CREDIT'), nullable=False)
    amount = db.Column(db.Numeric(16, 2), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<SystemAssetAccountItem %r, %r>' % (self.side, self.amount)


class UserLiabilityAccountItem(db.Model):
    __tablename__ = 'user_liability_account_item'

    id = db.Column(db.BigInteger, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('account_user.id'), nullable=False)
    user = db.relationship('AccountUser', backref=db.backref('liability_account_items', lazy='dynamic'))

    type = db.Column(db.Enum('TOTAL', 'AVAILABLE', 'FROZEN'), nullable=False)

    event_id = db.Column(db.BigInteger, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref=db.backref('liability_account_items', lazy='dynamic'))

    side = db.Column(db.Enum('DEBIT', 'CREDIT'), nullable=False)
    amount = db.Column(db.Numeric(16, 2), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<UserLiabilityAccountItem %r, %r, %r>' % (self.user_id, self.side, self.amount)


class UserCashBalance(db.Model):
    __tablename__ = 'user_cash_balance'

    id = db.Column(db.BigInteger, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('account_user.id'), nullable=False)
    user = db.relationship('AccountUser', backref=db.backref('cash_balance', lazy='dynamic'), uselist=False)

    total = db.Column(db.Numeric(16, 2), nullable=False, default=0)
    available = db.Column(db.Numeric(16, 2), nullable=False, default=0)
    frozen = db.Column(db.Numeric(16, 2), nullable=False, default=0)

    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return '<UserCashBalance %r: [%r, %r]>' % (self.user_id, self.total, self.available)


class UserCashBalanceLog(db.Model):
    __tablename__ = 'user_cash_balance_log'

    id = db.Column(db.BigInteger, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('account_user.id'), nullable=False)
    user = db.relationship('AccountUser', backref=db.backref('cash_balance_logs', lazy='dynamic'))

    event_id = db.Column(db.BigInteger, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref=db.backref('cash_balance_logs', lazy='dynamic'))

    total = db.Column(db.Numeric(16, 2), nullable=False, default=0)
    available = db.Column(db.Numeric(16, 2), nullable=False, default=0)
    frozen = db.Column(db.Numeric(16, 2), nullable=False, default=0)

    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return '<UserCashBalanceLog %r: [%r, %r]>' % (self.user_id, self.total, self.available)

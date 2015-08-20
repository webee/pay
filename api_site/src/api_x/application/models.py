# coding=utf-8
from __future__ import unicode_literals
from api_x import db
from datetime import datetime


class WithdrawState:
    PROCESSING = 'PROCESSING'
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'


class BankcardBin(db.Model):
    __tablename__ = 'bankcard_bin'

    id = db.Column(db.Integer, primary_key=True)

    card_no = db.Column(db.VARCHAR(21), nullable=False, unique=True)
    bank_code = db.Column(db.CHAR(9), nullable=False)
    bank_name = db.Column(db.VARCHAR(32), nullable=False)
    card_type = db.Column(db.Enum('DEBIT', 'CREDIT'), nullable=False)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'card_no': self.card_no,
            'bank_code': self.bank_code,
            'bank_name': self.bank_name,
            'card_type': self.card_type
        }

    def __repr__(self):
        return 'BankcardBin<%r, %r>' % (self.card_no, self.bank_name)


class Bankcard(db.Model):
    __tablename__ = 'bankcard'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    # 0-对私, 1-对公
    flag = db.Column(db.SmallInteger, nullable=False)
    card_no = db.Column(db.VARCHAR(21), nullable=False)
    card_type = db.Column(db.Enum('DEBIT', 'CREDIT'), nullable=False)
    acct_name = db.Column(db.CHAR(12), nullable=False)
    bank_code = db.Column(db.CHAR(9), nullable=False)
    province_code = db.Column(db.VARCHAR(12), nullable=False)
    city_code = db.Column(db.VARCHAR(12), nullable=False)
    bank_name = db.Column(db.VARCHAR(32), nullable=False)
    brabank_name = db.Column(db.VARCHAR(50), nullable=False)
    prcptcd = db.Column(db.CHAR(12), default='')

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'flag': self.flag,
            'card_no': self.card_no,
            'card_type': self.card_type,
            'acct_name': self.acct_name,
            'bank_code': self.bank_code,
            'province_code': self.province_code,
            'city_code': self.city_code,
            'bank_name': self.bank_name,
            'brabank_name': self.brabank_name,
            'prcptcd': self.prcptcd,
            'created_on': self.created_on
        }

    def __repr__(self):
        return 'Bankcard<%r, %r>' % (self.card_no, self.bank_name)


class UserWithdrawLog(db.Model):
    __tablename__ = 'user_withdraw_log'

    id = db.Column(db.Integer, primary_key=True)
    tx_sn = db.Column(db.CHAR(32), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    bankcard_id = db.Column(db.Integer, db.ForeignKey('bankcard.id'), nullable=False)

    amount = db.Column(db.Numeric(12, 2), nullable=False)
    actual_amount = db.Column(db.Numeric(12, 2))
    fee = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    state = db.Column(db.Enum(WithdrawState.PROCESSING, WithdrawState.FAILED, WithdrawState.SUCCESS), nullable=False)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

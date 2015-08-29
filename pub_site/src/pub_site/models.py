# coding=utf-8
from pub_site import db
from datetime import datetime


class LeaderApplication(db.Model):
    __tablename__ = 'leader_application'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.VARCHAR(32), nullable=False, unique=True)
    user_name = db.Column(db.VARCHAR(64), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<LeaderApplication %r@%r>' % (self.user_name, self.created_on)


class VerificationCode(db.Model):
    __tablename__ = 'verification_code'

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.VARCHAR(32), nullable=False)
    user_id = db.Column(db.VARCHAR(32), nullable=False)
    code = db.Column(db.VARCHAR(32), nullable=False)
    expire_at = db.Column(db.DateTime, nullable=False)

    # index
    __table_args__ = (db.UniqueConstraint('source', 'user_id', name='user_user_id_uniq_idx'),)


class PreferredCard(db.Model):
    __tablename__ = 'preferred_card'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.VARCHAR(32), nullable=False, unique=True)
    bankcard_id = db.Column(db.Integer, nullable=False)

    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class PayToLvyeRecord(db.Model):
    __tablename__ = 'pay_to_lvye_record'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.VARCHAR(32), nullable=False)
    pay_type = db.Column(db.Integer, nullable=False)
    name = db.Column(db.VARCHAR(100), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    desc = db.Column(db.VARCHAR(255), nullable=False)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

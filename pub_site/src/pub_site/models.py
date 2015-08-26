# coding=utf-8
from pub_site import db
from datetime import datetime


class LeaderApplication(db.Model):
    __tablename__ = 'leader_application'

    id = db.Column(db.Integer, primary_key=True)
    user_domain_name = db.Column(db.VARCHAR(32), nullable=False)
    user_id = db.Column(db.VARCHAR(32), nullable=False)
    user_name = db.Column(db.VARCHAR(64), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_domain_name', 'user_id', name='domain_user_id_uniq_idx'),)

    def __repr__(self):
        return '<LeaderApplication %r@%r>' % (self.user_id, self.created_on)


class IdentifyingCode(db.Model):
    __tablename__ = 'identifying_code'

    id = db.Column(db.Integer, primary_key=True)
    user_domain_name = db.Column(db.VARCHAR(32), nullable=False)
    user_id = db.Column(db.VARCHAR(32), nullable=False)
    code = db.Column(db.VARCHAR(32), nullable=False)
    expire_at = db.Column(db.DATETIME, nullable=False)

    __table_args__ = (db.UniqueConstraint('user_domain_name', 'user_id', name='domain_user_id_uniq_idx'),)


class PreferredCard(db.Model):
    __tablename__ = 'preferred_card'

    id = db.Column(db.Integer, primary_key=True)
    user_domain_name = db.Column(db.VARCHAR(32), nullable=False)
    user_id = db.Column(db.VARCHAR(32), nullable=False)
    bankcard_id = db.Column(db.Integer, nullable=False)

    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_domain_name', 'user_id', name='domain_user_id_uniq_idx'),)


class ZytOrder(db.Model):
    __tablename__ = 'zyt_order'

    id = db.Column(db.Integer, primary_key=True)
    user_domain_name = db.Column(db.VARCHAR(32), nullable=False)
    user_id = db.Column(db.VARCHAR(32), nullable=False)
    pay_type = db.Column(db.Integer, nullable=False)
    name = db.Column(db.VARCHAR(100), nullable=False)
    description = db.Column(db.VARCHAR(255), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_domain_name', 'user_id', name='domain_user_id_uniq_idx'),)

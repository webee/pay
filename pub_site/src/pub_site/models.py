# coding=utf-8
from pub_site import db
from datetime import datetime
from pub_site.constant import WithdrawState, PayToLvyeState


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

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # index
    __table_args__ = (db.UniqueConstraint('source', 'user_id', name='user_user_id_uniq_idx'),)


class PreferredCard(db.Model):
    __tablename__ = 'preferred_card'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.VARCHAR(32), nullable=False, unique=True)
    bankcard_id = db.Column(db.Integer, nullable=False)

    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class WithdrawRecord(db.Model):
    __tablename__ = 'withdraw_record'

    id = db.Column(db.Integer, primary_key=True)
    sn = db.Column(db.VARCHAR(40), nullable=False)
    user_id = db.Column(db.VARCHAR(32), nullable=False)
    bankcard_id = db.Column(db.Integer, nullable=False)
    phone_no = db.Column(db.VARCHAR(18), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    actual_amount = db.Column(db.Numeric(12, 2), nullable=False)
    fee = db.Column(db.Numeric(12, 2), nullable=False)

    state = db.Column(db.Enum(WithdrawState.REQUESTED, WithdrawState.FAILED, WithdrawState.SUCCESS),
                      nullable=False, default=WithdrawState.REQUESTED)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # index
    __table_args__ = (db.UniqueConstraint('sn', 'user_id', name='sn_user_id_uniq_idx'),)


class PayToLvyeRecord(db.Model):
    __tablename__ = 'pay_to_lvye_record'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.VARCHAR(32), nullable=False, unique=True)
    user_id = db.Column(db.VARCHAR(32), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    name = db.Column(db.VARCHAR(100), nullable=False)
    comment = db.Column(db.VARCHAR(255), nullable=False)

    sn = db.Column(db.VARCHAR(40))
    state = db.Column(db.Enum(PayToLvyeState.CREATED, PayToLvyeState.FAILED, PayToLvyeState.SUCCESS),
                      nullable=False, default=PayToLvyeState.CREATED)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

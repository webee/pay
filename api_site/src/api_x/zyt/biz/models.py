# coding=utf-8
from api_x import db
from datetime import datetime
from api_x.constant import TransactionType


class PaymentType:
    DIRECT = 'DIRECT'
    GUARANTEE = 'GUARANTEE'


class VirtualAccountSystem(db.Model):
    __tablename__ = 'virtual_account_system'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(32), nullable=False, unique=True)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<VirtualAccountSystem %r, %r>' % (self.id, self.name)


class TransactionRecord(db.Model):
    __tablename__ = 'transaction_record'

    id = db.Column(db.BigInteger, primary_key=True)
    sn = db.Column(db.CHAR(32))
    type = db.Column(db.Enum(TransactionType.PAYMENT, TransactionType.REFUND, TransactionType.WITHDRAW,
                             TransactionType.TRANSFER, TransactionType.PREPAID), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    comments = db.Column(db.VARCHAR(128), default='')
    state = db.Column(db.VARCHAR(32), nullable=False)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return '<Transaction %r, %r>' % (self.type, self.amount, self.state)


class TransactionStateLog(db.Model):
    __tablename__ = 'transaction_state_log'

    id = db.Column(db.BigInteger, primary_key=True)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction_record.id'), nullable=False)
    prev_state = db.Column(db.VARCHAR(32), nullable=False)
    state = db.Column(db.VARCHAR(32), nullable=False)

    event_id = db.Column(db.BigInteger, nullable=True, default=0L)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class UserTransaction(db.Model):
    __tablename__ = 'user_transaction'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('account_user.id'), nullable=False)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction_record.id'), nullable=False)
    tx_record = db.relationship('TransactionRecord', backref=db.backref('users', lazy='dynamic'))


class PaymentRecord(db.Model):
    __tablename__ = 'payment_record'

    id = db.Column(db.BigInteger, primary_key=True)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction_record.id'), nullable=False, unique=True)
    sn = db.Column(db.CHAR(32), nullable=False)

    type = db.Column(db.Enum(PaymentType.DIRECT, PaymentType.GUARANTEE), nullable=False)
    secured = db.Column(db.BOOLEAN, nullable=False, default=False)

    payer_id = db.Column(db.Integer, nullable=False)
    payee_id = db.Column(db.Integer, nullable=False)
    channel_id = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.VARCHAR(64), nullable=False)
    product_name = db.Column(db.VARCHAR(50), nullable=False)
    product_category = db.Column(db.VARCHAR(50), nullable=False)
    product_desc = db.Column(db.VARCHAR(50), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    refunded_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    es_name = db.Column(db.VARCHAR(32))
    es_sn = db.Column(db.VARCHAR(128))

    client_callback_url = db.Column(db.VARCHAR(128))
    client_notify_url = db.Column(db.VARCHAR(128))

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # index
    __table_args__ = (db.UniqueConstraint('channel_id', 'order_id', name='channel_order_id_uniq_idx'),)


class RefundRecord(db.Model):
    __tablename__ = 'refund_record'

    id = db.Column(db.BigInteger, primary_key=True)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction_record.id'), nullable=False, unique=True)
    sn = db.Column(db.CHAR(32), nullable=False)

    payment_sn = db.Column(db.CHAR(32), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)

    client_notify_url = db.Column(db.VARCHAR(128))

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class PrepaidRecord(db.Model):
    __tablename__ = 'prepaid_record'

    id = db.Column(db.BigInteger, primary_key=True)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction_record.id'), nullable=False, unique=True)
    sn = db.Column(db.CHAR(32), nullable=False)

    to_user_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Prepaid %r, %r>' % (self.user_id, self.amount)


class TransferRecord(db.Model):
    __tablename__ = 'transfer_record'

    id = db.Column(db.BigInteger, primary_key=True)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction_record.id'), nullable=False)
    sn = db.Column(db.CHAR(32), nullable=False)

    from_user_id = db.Column(db.Integer, nullable=False)
    to_user_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Bankcard(db.Model):
    __tablename__ = 'bankcard'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('account_user.id'), nullable=False)
    user = db.relationship('AccountUser', backref=db.backref('bankcards', lazy='dynamic'))

    # 0-对私, 1-对公
    flag = db.Column(db.SmallInteger, nullable=False)
    # 银行账号，对私必须是借记卡
    card_no = db.Column(db.VARCHAR(21), nullable=False)
    card_type = db.Column(db.Enum('DEBIT', 'CREDIT'), nullable=False)
    account_name = db.Column(db.VARCHAR(12), nullable=False)
    bank_code = db.Column(db.VARCHAR(12), nullable=False)
    province_code = db.Column(db.VARCHAR(12), nullable=False)
    city_code = db.Column(db.VARCHAR(12), nullable=False)
    bank_name = db.Column(db.VARCHAR(12), nullable=False)
    branch_bank_name = db.Column(db.VARCHAR(50), nullable=False)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class WithdrawRecord(db.Model):
    __tablename__ = 'withdraw_record'

    id = db.Column(db.BigInteger, primary_key=True)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction_record.id'), nullable=False)
    sn = db.Column(db.CHAR(32), nullable=False)

    from_user_id = db.Column(db.Integer, nullable=False)
    bankcard_id = db.Column(db.Integer, db.ForeignKey('bankcard.id'), nullable=False)

    amount = db.Column(db.Numeric(12, 2), nullable=False)

    client_notify_url = db.Column(db.VARCHAR(128))

    paybill_id = db.Column(db.VARCHAR(18))
    result = db.Column(db.VARCHAR(32))
    failure_info = db.Column(db.VARCHAR(255))

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

# coding=utf-8
from api_x import db
from datetime import datetime
from api_x.constant import TransactionType


class PaymentType:
    DIRECT = 'DIRECT'
    GUARANTEE = 'GUARANTEE'


class UserRole:
    FROM = 'FROM'
    TO = 'TO'
    GUARANTOR = 'GUARANTOR'


class VirtualAccountSystem(db.Model):
    __tablename__ = 'virtual_account_system'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(32), nullable=False, unique=True)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<VirtualAccountSystem %r, %r>' % (self.id, self.name)


class Transaction(db.Model):
    __tablename__ = 'transaction'

    id = db.Column(db.BigInteger, primary_key=True)
    sn = db.Column(db.CHAR(32))
    type = db.Column(db.Enum(TransactionType.PAYMENT, TransactionType.REFUND, TransactionType.WITHDRAW,
                             TransactionType.TRANSFER, TransactionType.PREPAID), nullable=False)

    channel_name = db.Column(db.VARCHAR(32), nullable=False)
    # 涉及到的总金额
    # 支付金额，退款金额，提现金额(+手续费)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    comments = db.Column(db.VARCHAR(128), default='')
    state = db.Column(db.VARCHAR(32), nullable=False)

    # need update on notify.
    vas_name = db.Column(db.VARCHAR(32), nullable=False, default='')
    vas_sn = db.Column(db.VARCHAR(128), nullable=False, default='')

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        super(Transaction, self).__init__(*args, **kwargs)
        self.__record = None

    @property
    def record(self):
        if self.__record:
            return self.__record
        if self.type == TransactionType.PAYMENT:
            self.__record = self.payment_record.one()
        elif self.type == TransactionType.REFUND:
            self.__record = self.refund_record.one()
        elif self.type == TransactionType.WITHDRAW:
            self.__record = self.withdraw_record.one()
        elif self.type == TransactionType.TRANSFER:
            self.__record = self.transfer_record.one()
        elif self.type == TransactionType.PREPAID:
            self.__record = self.prepaid_record.one()

        return self.__record

    def __repr__(self):
        return '<Transaction %s, %s, %s, %s>' % (self.type, str(self.amount), self.state, str(self.created_on))


class UserTransaction(db.Model):
    __tablename__ = 'user_transaction'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction.id'), nullable=False)
    tx = db.relationship('Transaction', backref=db.backref('users', lazy='dynamic'), lazy='joined')

    role = db.Column(db.Enum(UserRole.FROM, UserRole.GUARANTOR, UserRole.TO), nullable=False)

    def __repr__(self):
        return '<UserTransaction #%.6d %9s:%.5d, %.6d>' % (self.id, self.role, self.user_id, self.tx_id)


class TransactionStateLog(db.Model):
    __tablename__ = 'transaction_state_log'

    id = db.Column(db.BigInteger, primary_key=True)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction.id'), nullable=False)
    tx = db.relationship('Transaction', backref=db.backref('state_logs', lazy='dynamic'), lazy='joined')

    prev_state = db.Column(db.VARCHAR(32), nullable=False)
    state = db.Column(db.VARCHAR(32), nullable=False)

    event_id = db.Column(db.BigInteger, nullable=True, default=0L)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<TransactionStateLog %r: %r->%r@%r>' % (self.tx_id, self.prev_state, self.state, self.event_id)


class PaymentRecord(db.Model):
    __tablename__ = 'payment_record'

    id = db.Column(db.BigInteger, primary_key=True)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction.id'), nullable=False, unique=True)
    tx = db.relationship('Transaction', backref=db.backref('payment_record', lazy='dynamic'), lazy='joined')

    sn = db.Column(db.CHAR(32), nullable=False)

    type = db.Column(db.Enum(PaymentType.DIRECT, PaymentType.GUARANTEE), nullable=False)
    secured = db.Column(db.BOOLEAN, nullable=False, default=False)

    payer_id = db.Column(db.Integer, nullable=False)
    payee_id = db.Column(db.Integer, nullable=False)
    channel_id = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.VARCHAR(64), nullable=False)
    product_name = db.Column(db.VARCHAR(150), nullable=False)
    product_category = db.Column(db.VARCHAR(50), nullable=False)
    product_desc = db.Column(db.VARCHAR(350), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    refunded_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    client_callback_url = db.Column(db.VARCHAR(128))
    client_notify_url = db.Column(db.VARCHAR(128))
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    tried_times = db.Column(db.Integer, nullable=False, default=1)
    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # index
    __table_args__ = (db.UniqueConstraint('channel_id', 'order_id', name='channel_order_id_uniq_idx'),)

    def __repr__(self):
        return '<Payment %r>' % (self.id,)


class DuplicatedPaymentRecord(db.Model):
    __tablename__ = 'duplicated_payment_record'

    id = db.Column(db.BigInteger, primary_key=True)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction.id'), nullable=False, unique=True)
    tx = db.relationship('Transaction', backref=db.backref('duplicated_payment_record', lazy='dynamic'), lazy='joined')

    sn = db.Column(db.CHAR(32), nullable=False)

    vas_name = db.Column(db.VARCHAR(32), nullable=False, default='')
    vas_sn = db.Column(db.VARCHAR(128), nullable=False, default='')

    event_id = db.Column(db.BigInteger, nullable=True, default=0L)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class RefundRecord(db.Model):
    __tablename__ = 'refund_record'

    id = db.Column(db.BigInteger, primary_key=True)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction.id'), nullable=False, unique=True)
    tx = db.relationship('Transaction', backref=db.backref('refund_record', lazy='dynamic'), lazy='joined')

    sn = db.Column(db.CHAR(32), nullable=False)

    payment_sn = db.Column(db.CHAR(32), nullable=False)
    payment_state = db.Column(db.VARCHAR(32), nullable=False)
    payer_id = db.Column(db.Integer, nullable=False)
    payee_id = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.VARCHAR(64), nullable=False)

    amount = db.Column(db.Numeric(12, 2), nullable=False)
    client_notify_url = db.Column(db.VARCHAR(128))
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return '<Refund %r>' % (self.id,)


class PrepaidRecord(db.Model):
    __tablename__ = 'prepaid_record'

    id = db.Column(db.BigInteger, primary_key=True)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction.id'), nullable=False, unique=True)
    tx = db.relationship('Transaction', backref=db.backref('prepaid_record', lazy='dynamic'), lazy='joined')

    sn = db.Column(db.CHAR(32), nullable=False)

    to_user_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Prepaid %r>' % (self.user_id, self.amount)


class WithdrawRecord(db.Model):
    __tablename__ = 'withdraw_record'

    id = db.Column(db.BigInteger, primary_key=True)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction.id'), nullable=False)
    tx = db.relationship('Transaction', backref=db.backref('withdraw_record', lazy='dynamic'), lazy='joined')

    sn = db.Column(db.CHAR(32), nullable=False)

    from_user_id = db.Column(db.Integer, nullable=False)
    flag_card = db.Column(db.CHAR(1), nullable=False)
    card_type = db.Column(db.Enum('DEBIT', 'CREDIT'), nullable=False)
    card_no = db.Column(db.VARCHAR(21), nullable=False)
    acct_name = db.Column(db.VARCHAR(12), nullable=False)
    bank_code = db.Column(db.CHAR(9))
    province_code = db.Column(db.VARCHAR(12))
    city_code = db.Column(db.VARCHAR(12))
    bank_name = db.Column(db.VARCHAR(32), nullable=False)
    brabank_name = db.Column(db.VARCHAR(50))
    prcptcd = db.Column(db.CHAR(12))

    amount = db.Column(db.Numeric(12, 2), nullable=False)
    actual_amount = db.Column(db.Numeric(12, 2), nullable=False)
    fee = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    client_notify_url = db.Column(db.VARCHAR(128))

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return '<Withdraw %r>' % (self.id,)


class TransferRecord(db.Model):
    __tablename__ = 'transfer_record'

    id = db.Column(db.BigInteger, primary_key=True)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction.id'), nullable=False)
    tx = db.relationship('Transaction', backref=db.backref('transfer_record', lazy='dynamic'), lazy='joined')

    sn = db.Column(db.CHAR(32), nullable=False)

    from_user_id = db.Column(db.Integer, nullable=False)
    to_user_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Transfer %r>' % (self.id,)


# third party payments specific infos related to corresponding biz record.
# use it or not.
class PaymentRecordLianlianPayExtra(db.Model):
    __tablename__ = 'payment_record_lianlian_pay_extra'

    id = db.Column(db.BigInteger, primary_key=True)
    payment_record_id = db.Column(db.BigInteger, db.ForeignKey('payment_record.id'), nullable=False, unique=True)

    pay_type = db.Column(db.CHAR(1))

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class WithdrawRecordLianlianPayExtra(db.Model):
    __tablename__ = 'withdraw_record_lianlian_pay_extra'

    id = db.Column(db.BigInteger, primary_key=True)
    withdraw_record_id = db.Column(db.BigInteger, db.ForeignKey('withdraw_record.id'), nullable=False, unique=True)

    info_order = db.Column(db.VARCHAR(255))
    result_pay = db.Column(db.VARCHAR(12))
    settle_date = db.Column(db.VARCHAR(8))

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

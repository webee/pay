# coding=utf-8
from api_x import db
from pytoolbox.util.dbs import transactional
from datetime import datetime
from api_x.constant import TransactionType, PaymentChangeType
from api_x.config import etc
from api_x.utils import times
from api_x.zyt.biz import utils
from pytoolbox.util.log import get_logger
from api_x import db


logger = get_logger(__name__)


class PaymentType:
    DIRECT = 'DIRECT'
    GUARANTEE = 'GUARANTEE'


class UserRole:
    # FROM/TO是真正的资金方向
    # payment.TX_FROM, payment.TO
    # refund.FROM, refund.TX_TO
    FROM = 'FROM'
    TO = 'TO'

    GUARANTOR = 'GUARANTOR'
    # TX_FROM/TO仅仅表示交易的方向
    TX_FROM = 'TX_FROM'
    TX_TO = 'TX_TO'


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
    # 父tx
    super_id = db.Column(db.BigInteger, db.ForeignKey('transaction.id'), nullable=True, default=None)
    super = db.relationship('Transaction', remote_side=id, backref=db.backref('subs', lazy='dynamic'), lazy='joined')

    sn = db.Column(db.CHAR(32), unique=True)
    type = db.Column(db.Enum(TransactionType.PAYMENT, TransactionType.REFUND, TransactionType.WITHDRAW,
                             TransactionType.TRANSFER, TransactionType.PREPAID), nullable=False)

    channel_name = db.Column(db.VARCHAR(32), nullable=False)
    order_id = db.Column(db.VARCHAR(64), nullable=False, default='')
    # 涉及到的总金额
    # 支付金额，退款金额，提现金额(+手续费), 充值金额
    amount = db.Column(db.Numeric(16, 2), nullable=False)
    comments = db.Column(db.VARCHAR(128), default='')
    state = db.Column(db.VARCHAR(32), nullable=False)

    # need update on notify.
    vas_name = db.Column(db.VARCHAR(32), nullable=False, default='')
    vas_sn = db.Column(db.VARCHAR(128), nullable=False, default='')

    tried_times = db.Column(db.Integer, nullable=False, default=1)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        super(Transaction, self).__init__(*args, **kwargs)
        self.__record = None
        self.__source_sn = None
        self.__stack_sn_item = None

    @property
    def channel(self):
        from api_x.zyt.user_mapping import get_channel_by_name
        return get_channel_by_name(self.channel_name)

    @staticmethod
    def get_tx_from_hashed_sn(hashed_sn):
        try:
            tx_id, _hash = utils.aes_decrypt(hashed_sn).split('$', 1)
            return Transaction.query.get(tx_id), _hash
        except Exception as e:
            logger.warn('bad hashed sn: [{0}], [{1}]'.format(hashed_sn, e.message))
        return None, None

    @property
    def sn_with_expire_hash(self):
        now = times.timestamp()
        expired = now + etc.Biz.PAYMENT_CHECKOUT_VALID_SECONDS

        key = str(self.id) + str(self.tried_times) + etc.KEY
        data = str(int(expired))

        logger.info('hash sn: [%s], now: [%s], expired: [%s]' % (self.sn, now, expired))
        _hash = utils.aes_encrypt(data, key)

        return utils.aes_encrypt('%s$%s' % (self.id, _hash))

    def check_expire_hash(self, expire_hash):
        now = times.timestamp()
        key = str(self.id) + str(self.tried_times) + etc.KEY
        try:
            logger.info('try check sn: [%s], now: [%s], _hash: [%s]' % (self.sn, now, expire_hash))
            expired = long(utils.aes_decrypt(expire_hash, key))
        except Exception as _:
            return False

        timestamp = times.timestamp()
        logger.info('done check sn: [%s], timestamp: [%s], expired: [%s]' % (self.sn, timestamp, expired))
        return timestamp < expired

    @property
    def record(self):
        if hasattr(self, '_Transaction__record') and self.__record:
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

    def get_role(self, role):
        return self.users.filter_by(role=role).first()

    @property
    def source_sn(self):
        """ 表示当前使用的sn，参考 TransactionSnStack
        """
        # NOTE: Model类的属性名前面都添加了_<ClassName>前缀
        if hasattr(self, '_Transaction__source_sn') and self.__source_sn:
            return self.__source_sn
        return self.sn

    @source_sn.setter
    def source_sn(self, sn):
        self.__source_sn = sn

    @property
    def stack_sn_item(self):
        """ 表示当前使用的sn，参考 TransactionSnStack
        """
        # NOTE: Model类的属性名前面都添加了_<ClassName>前缀
        if hasattr(self, '_Transaction__stack_sn_item') and self.__stack_sn_item:
            return self.__stack_sn_item
        return self.sn

    @stack_sn_item.setter
    def stack_sn_item(self, sn):
        self.__stack_sn_item = sn

    def __repr__(self):
        return '<Transaction %s, %s, %s, %s>' % (self.type, str(self.amount), self.state, str(self.created_on))


class TransactionSnStack(db.Model):
    """ 用于记录tx的sn变化，比如支付时为防止evas异常，会定次定时变化sn,
    在回调中可以根据sn的记录来确定是否是同一笔交易。
    """
    __tablename__ = 'transaction_sn_stack'

    id = db.Column(db.BigInteger, primary_key=True)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction.id'), nullable=False)
    tx = db.relationship('Transaction', backref=db.backref('sns', lazy='dynamic'), lazy='joined')
    sn = db.Column(db.CHAR(32), index=True)
    generated_on = db.Column(db.DateTime, nullable=False)
    state = db.Column(db.VARCHAR(32), nullable=False)
    # 改变原因、类型
    change = db.Column(db.Enum(PaymentChangeType.EXPIRED, PaymentChangeType.AMOUNT, PaymentChangeType.INFO), default=None)

    pushed_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<TransactionSnStack %s, %s, %s, %s>' % (self.tx_id, self.sn, self.state, self.change)


class UserTransaction(db.Model):
    __tablename__ = 'user_transaction'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction.id'), nullable=False)
    tx = db.relationship('Transaction', backref=db.backref('users', lazy='dynamic'), lazy='joined')

    role = db.Column(db.Enum(UserRole.FROM, UserRole.GUARANTOR, UserRole.TO, UserRole.TX_FROM, UserRole.TX_TO), nullable=False)

    def __repr__(self):
        return '<UserTransaction #%.6d %9s:%.5d, %.6d>' % (self.id, self.role, self.user_id, self.tx_id)


class TransactionStateLog(db.Model):
    __tablename__ = 'transaction_state_log'

    id = db.Column(db.BigInteger, primary_key=True)
    group_id = db.Column(db.BigInteger, nullable=False, default=0L)
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

    payer_id = db.Column(db.Integer, nullable=False)
    payee_id = db.Column(db.Integer, nullable=False)
    channel_id = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.VARCHAR(64), nullable=False)
    origin = db.Column(db.VARCHAR(32), default=None)
    product_name = db.Column(db.VARCHAR(150), nullable=False)
    product_category = db.Column(db.VARCHAR(50), nullable=False)
    product_desc = db.Column(db.VARCHAR(350), nullable=False)
    amount = db.Column(db.Numeric(16, 2), nullable=False)
    real_amount = db.Column(db.Numeric(16, 2), nullable=False, default=0)
    paid_amount = db.Column(db.Numeric(16, 2), nullable=False, default=0)
    refunded_amount = db.Column(db.Numeric(16, 2), nullable=False, default=0)
    client_callback_url = db.Column(db.VARCHAR(128))
    client_notify_url = db.Column(db.VARCHAR(128))
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    tried_times = db.Column(db.Integer, nullable=False, default=1)
    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # index
    __table_args__ = (db.UniqueConstraint('channel_id', 'order_id', 'origin', name='channel_order_id_origin_uniq_idx'),)

    def is_finished(self):
        return self.real_amount == self.paid_amount - self.refunded_amount

    @transactional
    def add_refund(self, refund_record, event_id):
        from api_x.constant import PaymentTxState
        from api_x.zyt.biz.transaction import transit_transaction_state
        self.refunded_amount += refund_record.amount
        # 全部金额都退款，则状态为已退款
        is_refunded = self.paid_amount == self.refunded_amount

        if self.tx.state == PaymentTxState.REFUNDING:
            if is_refunded:
                transit_transaction_state(self.tx_id, PaymentTxState.REFUNDING, PaymentTxState.REFUNDED, event_id)
            else:
                transit_transaction_state(self.tx_id, PaymentTxState.REFUNDING, refund_record.payment_state, event_id)
        db.session.add(self)

        super_tx = self.tx.super
        if super_tx and super_tx.type == TransactionType.PAYMENT:
            super_payment = super_tx.record
            super_payment.add_refund(refund_record, event_id)

    @transactional
    def add_paid(self, amount):
        self.paid_amount += amount
        db.session.add(self)

        super_tx = self.tx.super
        if super_tx and super_tx.type == TransactionType.PAYMENT:
            super_payment = super_tx.record
            super_payment.add_paid(amount)

    def __repr__(self):
        return '<Payment %r, %r->%r$%r:%r:%r/%r>' % (self.id, self.payer_id, self.payee_id,
                                                     self.amount, self.real_amount, self.paid_amount, self.refunded_amount)


class DuplicatedPaymentRecord(db.Model):
    __tablename__ = 'duplicated_payment_record'

    id = db.Column(db.BigInteger, primary_key=True)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction.id'), nullable=False, unique=True)
    tx = db.relationship('Transaction', backref=db.backref('duplicated_payment_record', lazy='dynamic'), lazy='joined')

    sn = db.Column(db.CHAR(32), nullable=False)
    source = db.Column(db.Enum(TransactionType.PAYMENT, TransactionType.PREPAID), nullable=False)

    vas_name = db.Column(db.VARCHAR(32), nullable=False, default='')
    vas_sn = db.Column(db.VARCHAR(128), nullable=False, default='')

    event_id = db.Column(db.BigInteger, nullable=False, default=0L)

    status = db.Column(db.SmallInteger, nullable=False, default=0)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


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

    amount = db.Column(db.Numeric(16, 2), nullable=False)
    client_notify_url = db.Column(db.VARCHAR(128))
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return '<Refund %r, %r<-%r$%r>' % (self.id, self.payer_id, self.payee_id, self.amount)


class PrepaidRecord(db.Model):
    __tablename__ = 'prepaid_record'

    id = db.Column(db.BigInteger, primary_key=True)
    tx_id = db.Column(db.BigInteger, db.ForeignKey('transaction.id'), nullable=False, unique=True)
    tx = db.relationship('Transaction', backref=db.backref('prepaid_record', lazy='dynamic'), lazy='joined')

    sn = db.Column(db.CHAR(32), nullable=False)

    to_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(16, 2), nullable=False)

    client_callback_url = db.Column(db.VARCHAR(128))
    client_notify_url = db.Column(db.VARCHAR(128))
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @property
    def payer_id(self):
        return self.to_id

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

    amount = db.Column(db.Numeric(16, 2), nullable=False)
    actual_amount = db.Column(db.Numeric(16, 2), nullable=False)
    fee = db.Column(db.Numeric(16, 2), nullable=False, default=0)

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

    from_id = db.Column(db.Integer, nullable=False)
    to_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(16, 2), nullable=False)

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

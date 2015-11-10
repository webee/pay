# coding=utf-8
from api_x import db
from datetime import datetime

from api_x.constant import TransactionType


class DebitNoteDate(db.Model):
	__tablename__ = 'debit_note_date'

	id = db.Column(db.Integer, primary_key=True)

	state = db.Column(db.Boolean, nullable=False, default=False)
	date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	vas_name = db.Column(db.VARCHAR(32), nullable=False)

	def __repr__(self):
		return '<DebitNoteDate %r>' % (self.id,self.date,self.state)


class DebitNoteDetail(db.Model):
	__tablename__ = 'debit_note_detail'

	id = db.Column(db.BigInteger, primary_key=True)
	sn = db.Column(db.CHAR(32), nullable=False)
	vas_name = db.Column(db.VARCHAR(32), nullable=False)
	amount = db.Column(db.Numeric(12, 2), nullable=False)
	order_id = db.Column(db.VARCHAR(64), nullable=False, default='')
	state = db.Column(db.Boolean, nullable=False, default=False)  # False:Lvyeok    True:LLok
	valid = db.Column(db.Boolean, nullable=False, default=False)  # False:checking  True:ok
	created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	type = db.Column(db.Enum(TransactionType.PAYMENT, TransactionType.REFUND), nullable=False)


	def __repr__(self):
		return '<DebitNoteDetail %r, %r, %r, %r, %r, %r, %r, %r>' % (self.id, self.sn,self.vas_name,self.amount,self.order_id,self.state,self.valid,self.created_on)

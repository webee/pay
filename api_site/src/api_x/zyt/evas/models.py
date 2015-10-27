# coding=utf-8
from __future__ import unicode_literals, print_function

from api_x import db
from datetime import datetime


class EvasNotifyLog(db.Model):
    __tablename__ = 'evas_notify_log'

    id = db.Column(db.BigInteger, primary_key=True)
    vas_name = db.Column(db.VARCHAR(32), nullable=False)

    event = db.Column(db.VARCHAR(32), nullable=False)
    content = db.Column(db.UnicodeText(), default="")

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<EvasNotifyLog %r, %r>' % (self.side, self.amount)

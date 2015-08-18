# coding=utf-8
from api_x import db
from datetime import datetime


class Bankcard(db.Model):
    __tablename__ = 'bankcard'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    # 0-对私, 1-对公
    flag = db.Column(db.SmallInteger, nullable=False)
    card_no = db.Column(db.VARCHAR(21), nullable=False)
    card_type = db.Column(db.Enum('DEBIT', 'CREDIT'), nullable=False)
    account_name = db.Column(db.VARCHAR(12), nullable=False)
    bank_code = db.Column(db.VARCHAR(12), nullable=False)
    province_code = db.Column(db.VARCHAR(12), nullable=False)
    city_code = db.Column(db.VARCHAR(12), nullable=False)
    bank_name = db.Column(db.VARCHAR(12), nullable=False)
    branch_bank_name = db.Column(db.VARCHAR(50), nullable=False)

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

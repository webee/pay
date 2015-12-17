# coding=utf-8
from pytoolbox.util.dbs import transactional
from pub_site import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class DomainUser(db.Model):
    __tablename__ = 'domain_user'
    id = db.Column(db.Integer, primary_key=True)
    user_domain_name = db.Column(db.VARCHAR(32), nullable=False)
    username = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(18), nullable=False)
    password_hash = db.Column("password", db.String(128))

    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    # index
    __table_args__ = (db.UniqueConstraint('user_domain_name', 'username', name='user_domain_user_name_uniq_idx'),)

    def __init__(self, **kargs):
        super(DomainUser, self).__init__(**kargs)

    @property
    def password(self):
        """密码不可读"""
        raise AttributeError('password is not an readable attribute')

    @password.setter
    def password(self, password):
        """只保存密码的hash值"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """校验密码"""
        return check_password_hash(self.password_hash, password)

    @transactional
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __repr__(self):
        return '<User %r>' % self.username


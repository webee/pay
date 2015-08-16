# coding=utf-8
from contextlib import contextmanager
from functools import wraps
from api_x import db


@contextmanager
def require_transaction_context():
    with db.session.begin(subtransactions=True):
        yield
        db.session.flush()


def transactional(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with require_transaction_context():
            return func(*args, **kwargs)

    return wrapper

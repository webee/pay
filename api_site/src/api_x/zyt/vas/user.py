# coding=utf-8
from api_x import db
from api_x.zyt.vas.models import AccountUser, UserCashBalance
from api_x.dbs import transactional


@transactional
def create_user():
    user = AccountUser()
    cash_balance = UserCashBalance(user=user)

    db.session.add(user)
    db.session.add(cash_balance)

    return user


def get_user_by_id(id):
    return AccountUser.query.get(id)


def get_user_cash_balance(user_id):
    return UserCashBalance.query.filter_by(user_id=user_id).one()

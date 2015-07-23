# coding=utf-8
from __future__ import unicode_literals

from . import make_celery_app
from tools.mylog import get_logger
from api.payment.confirm_pay import list_all_expired_payments, confirm_payment
from api.account.balance import list_users_with_unsettled_cash
from api.account.balance import settle_user_account_balance

logger = get_logger(__name__)
app = make_celery_app('pay', 'api.task.config')


@app.task
def confirm_to_pay_all():
    pay_records = list_all_expired_payments
    for pay_record in pay_records:
        _ = confirm_pay.apply_async(args=[pay_record], queue='confirm_pay', routing_key='confirm_pay')
    return len(pay_records)


@app.task(ignore_result=False, queue='confirm_pay', routing_key='confirm_pay')
def confirm_pay(pay_record):
    return confirm_payment(pay_record)


@app.task
def settle_all_cash_balance():
    users = list_users_with_unsettled_cash()
    for user in users:
        _ = settle_user_cash_balance.apply_async(args=[user.account_id, user.high_id],
                                                 queue='settle_cash_balance', routing_key='settle_cash_balance')
    return len(users)


@app.task(ignore_result=True, queue='settle_cash_balance', routing_key='settle_cash_balance')
def settle_user_cash_balance(account_id, high_id=None):
    settle_user_account_balance(account_id, 'cash', high_id)

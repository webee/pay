# coding=utf-8
from __future__ import unicode_literals
from . import make_celery_app
from tools.mylog import get_logger
from api.payment.confirm_pay import list_all_expired_payments
from api.payment.confirm_pay import confirm_payment_by_id
from api.account.account.dba import list_users_with_unsettled_cash
from api.account.account.balance import settle_user_account_balance

logger = get_logger(__name__)
app = make_celery_app('pay')


@app.task
def confirm_to_pay_all():
    payments = list_all_expired_payments()
    for payment in payments:
        _ = confirm_pay.apply_async(args=[payment.id], queue='confirm_pay', routing_key='confirm_pay')
    return len(payments)


@app.task(ignore_result=False, queue='confirm_pay', routing_key='confirm_pay')
def confirm_pay(payment_id):
    return confirm_payment_by_id(payment_id)


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


@app.task(ignore_result=True, queue='withdraw_notify', routing_key='withdraw_notify')
def withdraw_notify(url, params, next_time, count=1):
    from api.account.withdraw.notify import notify_client
    do_notify_client(refund_notify, notify_client, url, params, next_time, count)


@app.task(ignore_result=True, queue='refund_notify', routing_key='refund_notify')
def refund_notify(url, params, next_time, count=1):
    from api.commons.notify import notify_client
    do_notify_client(refund_notify, notify_client, url, params, next_time, count)


def do_notify_client(task, notify_client, url, params, next_time, count):
    from datetime import datetime, timedelta

    # max execute 30 times.
    if count > 30:
        return

    now = datetime.now()
    if now < next_time:
        task.delay(url, params, next_time, count=count)

    if not notify_client(url, params):
        # retry every two minutes.
        next_time = timedelta(minutes=2)
        task.delay(url, params, next_time, count=count + 1)

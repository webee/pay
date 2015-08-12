# -*- coding: utf-8 -*-
from .withdraw import succeed_withdraw, fail_withdraw


def notify_result_to_charged_withdraw(charged_withdraw_id, is_successful):
    if is_successful:
        succeed_withdraw(charged_withdraw_id)
    else:
        fail_withdraw(charged_withdraw_id)
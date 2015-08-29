# -*- coding: utf-8 -*-
from api_x.zyt.vas import user


def get_user_cash_balance(account_user_id):
    # FIXME:
    # 在application成为真正独立子系统时，这里应该使用api交互
    return user.get_user_cash_balance(account_user_id)

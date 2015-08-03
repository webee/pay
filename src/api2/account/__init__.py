# -*- coding: utf-8 -*-
import dba


def get_account_by_user_info(client_id, user_id):
    return dba.get_account_by_user_info(client_id, user_id)


def get_account_by_id(account_id):
    return dba.get_account_by_id(account_id)


def find_or_create_account(client_id, user_id):
    return find_or_create_account(client_id, user_id)
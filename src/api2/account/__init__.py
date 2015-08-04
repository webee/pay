# -*- coding: utf-8 -*-
import dba


def get_account_by_user_info(client_id, user_id):
    return dba.find_account_by_user_info(client_id, user_id)


def get_account_by_id(account_id):
    return dba.find_account_by_id(account_id)


def find_or_create_account(client_id, user_id):
    return dba.find_or_create_account(client_id, user_id)


def new_account(client_id, user_id, desc='Normal Account'):
    return dba.create_account(client_id, user_id, desc)

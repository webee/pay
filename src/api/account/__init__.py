# -*- coding: utf-8 -*-
import dba


def get_account_by_user_info(user_domain_id, user_id):
    return dba.find_account_by_user_info(user_domain_id, user_id)


def get_account_by_id(account_id):
    return dba.find_account_by_id(account_id)


def find_or_create_account(user_domain_id, user_id):
    return dba.find_or_create_account(user_domain_id, user_id)


def get_secured_account_id():
    return dba.find_secured_account()['id']


def find_user_domain_id_by_channel(channel_id):
    return dba.find_user_domain_id_by_channel(channel_id)
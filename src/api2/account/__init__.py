# -*- coding: utf-8 -*-
from .dba import get_account


def get_account_id(client_id, user_id):
    return get_account(client_id, user_id)['id']


def find_or_create_account(client_id, user_id):
    return find_or_create_account(client_id, user_id)
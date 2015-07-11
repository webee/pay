# -*- coding: utf-8 -*-

class Order(object):
    def __init__(self, no, name, desc, created_on):
        self.no = no
        self.name = name
        self.desc = desc
        self.created_on = created_on


def save_pay_info(user_id, order, amount):
    pass


def build_pay_url(pay_id):
    pass

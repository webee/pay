# coding=utf-8
import random


def generate_sn(merchant_id, order_no):
    return '{0}.{1}.{2}'.format(merchant_id, order_no, random.randint(0, 99))
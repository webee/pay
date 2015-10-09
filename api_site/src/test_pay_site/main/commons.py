# coding=utf-8
from datetime import datetime
import random


def generate_sn(merchant_id, order_no):
    n = datetime.utcnow()
    return '{0}.{1}.{2}{3}'.format(merchant_id, order_no, n.second, random.randint(0, 99))
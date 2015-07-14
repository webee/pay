# coding=utf-8
from __future__ import unicode_literals


class BankCard(object):
    def __init__(self, flag_card, card_no, acct_name,
                 bank_code, province_code, city_code,
                 brabank_name):
        # 对公对私标志, 0-对私，1-对公
        self.flag_card = flag_card
        # 银行账号, 对私必须是借记卡
        self.card_no = card_no
        # 用户银行账号姓名
        self.acct_name = acct_name
        # 银行编码
        self.bank_code = bank_code
        # 开户行所有省编码
        self.province_code = province_code
        # 开户行所在市编码
        self.city_code = city_code
        # 开户支行名称
        self.brabank_name = brabank_name


def get_bank_card(account_id, bank_card_id):
    return BankCard(
        flag_card='0',
        card_no='6222081202007688888',
        acct_name='张三',
        bank_code='03050001',
        province_code='',
        city_code='110001',
        brabank_name='运城车站支行',
    )

# coding=utf-8
from __future__ import unicode_literals
from tools.dbi import from_db


class BankCard(dict):
    def __init__(self, flag_card, card_no, acct_name,
                 bank_code, province_code, city_code,
                 brabank_name, updated_on, created_on):
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

        self.updated_on = updated_on
        self.created_on = created_on

        self.update(self.__dict__)


def _gen_bankcard_from_dict(bankcard):
    return BankCard(
        flag_card=bankcard['flag'],
        card_no=bankcard['card_no'],
        acct_name=bankcard['account_name'],
        bank_code=bankcard['bank_code'],
        province_code=bankcard['province_code'],
        city_code=bankcard['city_code'],
        brabank_name=bankcard['branch_bank_name'],
        created_on=bankcard['created_on'],
        updated_on=bankcard['updated_on'],
    )


def get_bankcard(account_id, bankcard_id):
    db = from_db()
    bankcard = db.get('select * from bankcard where account_id=%(account_id)s and id=%(bankcard_id)s',
                      account_id=account_id, bankcard_id=bankcard_id)
    if bankcard:
        return _gen_bankcard_from_dict(bankcard)


def get_user_bankcards(account_id):
    db = from_db()
    bankcards = db.list('select * from bankcard where account_id=%(account_id)s', account_id=account_id)

    return [_gen_bankcard_from_dict(bankcard) for bankcard in bankcards]

# coding=utf-8
from pytoolbox.util.dbs import transactional
from api_x import db
from api_x.constant import BankAccountType
from .models import BankcardBin, Bankcard, UserWithdrawLog


@transactional
def add_bankcard_bin(info):
    card_no = info.card_no
    bank_code = info.bank_code
    bank_name = info.bank_name
    card_type = info.card_type

    bankcard_bin = BankcardBin(card_no=card_no, bank_code=bank_code, bank_name=bank_name, card_type=card_type)
    db.session.add(bankcard_bin)


@transactional
def add_bankcard(user_id, bankcard_info):
    fields = {
        'user_id': user_id,
        'card_no': bankcard_info.card_no,
        'card_type': bankcard_info.card_type,
        'acct_name': bankcard_info.acct_name,
        'flag': BankAccountType.CORPORATE if bankcard_info.is_corporate_account else BankAccountType.PRIVATE,
        'bank_code': bankcard_info.bank_code,
        'province_code': bankcard_info.province_code,
        'city_code': bankcard_info.city_code,
        'bank_name': bankcard_info.bank_name,
        'brabank_name': bankcard_info.brabank_name,
    }
    bankcard = Bankcard(**fields)
    db.session.add(bankcard)

    return bankcard.id


@transactional
def add_user_withdraw_log(user_id, tx_sn, bankcard_id, amount, fee, state):
    fields = {
        'user_id': user_id,
        'tx_sn': tx_sn,
        'bankcard_id': bankcard_id,
        'amount': amount,
        'fee': fee,
        'state': state
    }
    user_withdraw_log = UserWithdrawLog(**fields)
    db.session.add(user_withdraw_log)


def get_bankcard_bin(card_no):
    bankcard_bin = BankcardBin.query.filter_by(card_no=card_no).first()

    return bankcard_bin


def query_all_bankcards(user_id):
    return Bankcard.query.filter_by(user_id=user_id).all()


def query_bankcard_by_id(id):
    return Bankcard.query.get(id)


def query_user_withdraw_logs(user_id, dt=None):
    query = UserWithdrawLog.query.filter_by(user_id=user_id)
    if dt:
        query = query.filter(UserWithdrawLog.created_on > dt)
    return query.all()

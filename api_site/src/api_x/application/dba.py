# coding=utf-8
from api_x.application.error import BankcardNotFoundError
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
def bind_bankcard(user_id, bankcard_info):
    bankcard = Bankcard.query.filter_by(user_id=user_id, card_no=bankcard_info.card_no).first()
    if bankcard is None:
        bankcard = Bankcard()

    bankcard.user_id = user_id,
    bankcard.card_no = bankcard_info.card_no,
    bankcard.card_type = bankcard_info.card_type,
    bankcard.acct_name = bankcard_info.acct_name,
    bankcard.flag = BankAccountType.CORPORATE if bankcard_info.is_corporate_account else BankAccountType.PRIVATE,
    bankcard.bank_code = bankcard_info.bank_code,
    bankcard.province_code = bankcard_info.province_code,
    bankcard.city_code = bankcard_info.city_code,
    bankcard.bank_name = bankcard_info.bank_name,
    bankcard.brabank_name = bankcard_info.brabank_name,
    bankcard.is_bounded = True

    db.session.add(bankcard)

    return bankcard

@transactional
def unbind_bankcard(user_id, bankcard_id):
    bankcard = Bankcard.query.get(bankcard_id)

    if bankcard is None or bankcard.user_id != user_id:
        raise BankcardNotFoundError()

    bankcard.is_bounded = False
    db.session.add(bankcard)


@transactional
def add_user_withdraw_log(user_id, tx_sn, bankcard_id, amount, actual_amount, fee, state):
    fields = {
        'user_id': user_id,
        'tx_sn': tx_sn,
        'bankcard_id': bankcard_id,
        'amount': amount,
        'actual_amount': actual_amount,
        'fee': fee,
        'state': state
    }
    user_withdraw_log = UserWithdrawLog(**fields)
    db.session.add(user_withdraw_log)


def get_bankcard_bin(card_no):
    bankcard_bin = BankcardBin.query.filter_by(card_no=card_no).first()

    return bankcard_bin


def query_all_bankcards(user_id):
    return Bankcard.query.filter_by(user_id=user_id, is_bounded=True).all()


def query_bankcard_by_id(id):
    return Bankcard.query.get(id)


def query_user_withdraw_logs(user_id, dt=None):
    query = UserWithdrawLog.query.filter_by(user_id=user_id)
    if dt:
        query = query.filter(UserWithdrawLog.created_on > dt)
    return query.all()

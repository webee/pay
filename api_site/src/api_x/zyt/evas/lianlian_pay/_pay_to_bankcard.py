# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .api_access import request
from api_x.utils.times import now_to_str
from api_x.config import lianlian_pay
from ..error import EvasError
from api_x.constant import BankcardType
from pytoolbox.util.sign import SignType


def pay_to_bankcard(no_order, money_order, info_order, notify_url,
                    flag_card, card_type, card_no, acct_name,
                    bank_code='', province_code='', city_code='', brabank_name='',
                    prcptcd=''):
    _validate_bankcard(flag_card, card_type, bank_code, province_code, city_code, brabank_name, prcptcd)

    params = {
        'platform': lianlian_pay.PLATFORM,
        'oid_partner': lianlian_pay.OID_PARTNER,
        'sign_type': SignType.RSA,
        'no_order': no_order,
        'dt_order': now_to_str(),
        'money_order': money_order,
        'info_order': info_order,
        'flag_card': unicode(flag_card),
        'card_no': card_no,
        'acct_name': acct_name,
        'bank_code': bank_code,
        'province_code': province_code,
        'city_code': city_code,
        'brabank_name': brabank_name,
        'prcptcd': prcptcd,
        'notify_url': notify_url,
        'api_version': lianlian_pay.PayToBankcard.VERSION
    }
    return request(lianlian_pay.PayToBankcard.URL, params)


def _validate_bankcard(flag_card, card_type, bank_code,
                       province_code, city_code, brabank_name,
                       prcptcd):
    # 对私必须是借记卡
    if not _is_to_corporate(flag_card) and card_type != BankcardType.DEBIT:
        raise PayToBankcardError('对私必须是借记卡')

    # 对公 bank_code必须传
    if _is_to_corporate(flag_card) and not bank_code:
        raise PayToBankcardError('对公bank_code必传')

    # prcptcd若传，则省市支行可以不传
    if prcptcd:
        return

    # province_code, city_code, brabank_name,
    # 其他银行必须传
    if not province_code or not city_code or not brabank_name:
        # 建行 (对公打款)可以不传
        if _is_to_corporate(flag_card) and bank_code == '01050000':
            return

        # 工、农、中、招、光大、浦发(对私打款),
        if not _is_to_corporate(flag_card)\
                and bank_code in ['01020000', '01030000', '01040000',
                                  '01080000', '03030000', '03100000']:
            return
        raise PayToBankcardError('需要province_code, city_code, brabank_name')


def _is_to_corporate(flag_card):
    flag = str(flag_card)
    # 0-对私，1-对公
    return flag == '1'


def is_success_result(result):
    return result == lianlian_pay.PayToBankcard.Result.SUCCESS


def is_failed_result(result):
    return result == lianlian_pay.PayToBankcard.Result.FAILURE


# errors
class PayToBankcardError(EvasError):
    def __init__(self, message):
        super(PayToBankcardError, self).__init__(message)

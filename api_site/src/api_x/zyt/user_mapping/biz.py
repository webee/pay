# coding=utf-8
from api_x.config import etc as config
from api_x.zyt.user_mapping import get_user_map_by_account_user_id


def gen_payment_user_id(user_id, domain_id):
    return '%s%s.%d' % (config.Biz.TX_SN_PREFIX, user_id, domain_id)


def gen_payment_user_id_by_account_user_id(account_user_id):
    user_map = get_user_map_by_account_user_id(account_user_id)
    return '%s%s.%d' % (config.Biz.TX_SN_PREFIX, user_map.user_id, user_map.user_domain_id)
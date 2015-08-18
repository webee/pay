# coding=utf-8


def is_duplicated_notify(tx, vas_name, vas_sn):
    return vas_name == tx.vas_name and vas_sn == tx.vas_sn

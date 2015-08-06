# coding=utf-8
from . import _dba
from ._bookkeeping import SOURCE_TYPE_TABLE_MAP


def get_user_cash_account_records(account_id, page_no, page_size):
    offset = (page_no - 1) * page_size
    limit = page_size
    records = _dba.get_user_cash_account_log(account_id, offset, limit)

    # get source_type and source_id
    source_type_ids = {}
    for record in records:
        source_type = record.source_type.split(':', 1)[0]
        ids = source_type_ids.setdefault(source_type, [])
        ids.append(record.source_id)

    # get order infos.
    orders_info = {}
    for source_type, ids in source_type_ids.items():
        table_name = SOURCE_TYPE_TABLE_MAP[source_type]
        orders = _dba.get_orders_info_by_ids(table_name, ids)
        for order in orders:
            orders_info[order.id] = order

    return records, orders_info

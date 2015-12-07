# coding=utf-8
from pytoolbox.util.dbs import transactional
from api_x import db
from api_x.zyt.evas.utils import generate_sn
from .models import EvasAlipayBatchRefundRecord


@transactional
def get_or_create_alipay_batch_refund_record(trade_no, refund_tx_sn):
    record = EvasAlipayBatchRefundRecord.query.filter_by(refund_tx_sn=refund_tx_sn).first()
    if record is None:
        batch_no = generate_sn()
        record = EvasAlipayBatchRefundRecord(batch_no=batch_no, trade_no=trade_no, refund_tx_sn=refund_tx_sn)
        db.session.add(record)
    return record


def get_alipay_batch_refund_record(batch_no, trade_no):
    return EvasAlipayBatchRefundRecord.query.filter_by(batch_no=batch_no, trade_no=trade_no).first()

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sqlalchemy.sql import text
import os
import paramiko
import datetime
from api_x import db

from api_x.debit_note.models import DebitNoteDate, DebitNoteDetail
from api_x.config import lianlian_pay as config


def get_tx_by_orderid(orderid="OD150901103401SN4WWT"):
    if not orderid: return
    sql1 = """select * from transaction where order_id="%s";""" % orderid
    s = text(sql1)
    results = db.session.execute(s).fetchall()
    if not results:
        return

    ret = []
    for tx in results:
        if tx.type == "PAYMENT":
            sql2 = """select * from payment_record where tx_id=%s; """ % tx.id
        elif tx.type == "REFUND":
            sql2 = """select * from refund_record where tx_id=%s; """ % tx.id
        print sql2
        s = text(sql2)
        record = db.session.execute(s).fetchone()
        payer_id = record.payer_id
        payee_id = record.payee_id
        payer, payee = payer_id, payee_id
        #	sql3 = """select * from  user_mapping where account_user_id in (%s,%s);  """%(payer_id,payee_id)
        #	s = text(sql3)
        #	aus = db.session.execute(s).fetchall()
        #	payer,payee = "",""
        #	for au in aus:
        #		if au.account_user_id == payer_id:
        #			payer = au.user_id
        #		elif au.account_user_id == payee_id:
        #			payee = au.user_id
        tmpd = {}
        tmpd["created_on"] = tx.created_on
        tmpd["payer"] = payer
        tmpd["payee"] = payee
        tmpd["type"] = tx.type
        tmpd["state"] = tx.state
        tmpd["comments"] = tx.comments
        tmpd["sn"] = tx.sn
        tmpd["tx_id"] = tx.id
        tmpd["amount"] = tx.amount
        tmpd["orderid"] = tx.order_id
        ret.append(tmpd)
    return ret


def get_tx_detail_by_txid(txid=""):
    if not txid: return (None, None)
    sql1 = """select tsl.event_id,tsl.created_on,prev_state,state,amount,type,vas_name from transaction_state_log tsl left join event e on tsl.event_id=e.id  where tsl.tx_id = %s;""" % txid
    s = text(sql1)
    results = db.session.execute(s).fetchall()
    if not results: return (None, None)
    ret = []
    eventids = []
    for result in results:
        tmpd = {}
        tmpd["created_on"] = result.created_on
        tmpd["prev_state"] = result.prev_state
        tmpd["state"] = result.state
        tmpd["amount"] = result.amount
        tmpd["type"] = result.type
        tmpd["vas_name"] = result.vas_name
        tmpd["event_id"] = result.event_id
        eventids.append(result.event_id)
        ret.append(tmpd)
    accountdata = get_user_cash_balance(eventids)
    return ret, accountdata


def get_user_cash_balance(eventids):
    if not eventids: return
    sql1 = """ select * from user_cash_balance_log where event_id in (%s); """ % (",".join([str(i) for i in eventids]))
    s = text(sql1)
    results = db.session.execute(s).fetchall()
    if not results: return
    ret = []
    for result in results:
        tmpd = {}
        tmpd["created_on"] = result.updated_on
        tmpd["user_id"] = result.user_id
        tmpd["event_id"] = result.event_id
        tmpd["balance2"] = result.total
        tmpd["balance1"] = getlastbalance(result.id, result.user_id)
        tmpd["amount"] = None if tmpd["balance1"] == None else tmpd["balance2"] - tmpd["balance1"]
        ret.append(tmpd)
    return ret


def getlastbalance(id, userid):
    sql1 = """ select * from user_cash_balance_log where user_id = %s and id < %s order by id desc limit 1; """ % (
        userid, id)
    s = text(sql1)
    result = db.session.execute(s).fetchone()
    if not result:
        return
    else:
        return result.total


def getrecon():
    data = get_recondetail()
    date = get_recondate()
    return data, date


def get_recondetail():
    data = []
    dnds = db.session.query(DebitNoteDetail).filter(DebitNoteDetail.valid == False).all()
    for dnd in dnds:
        print dnd
        tmp = {}
        tmp["sn"] = dnd.sn
        tmp["ll_vasname"] = dnd.vas_name
        if not dnd.state:
            tmp["ly_date"] = dnd.created_on
            tmp["ly_type"] = dnd.type
            tmp["ly_orderid"] = dnd.order_id
            tmp["ly_amount"] = dnd.amount
            tmp["ll_date"] = "第三方支付记录缺失"
            tmp["ll_type"] = ""
            tmp["ll_orderid"] = ""
            tmp["ll_amount"] = ""
        else:
            tmp["ly_date"] = "自游通记录缺失"
            tmp["ly_type"] = ""
            tmp["ly_orderid"] = ""
            tmp["ly_amount"] = ""
            tmp["ll_date"] = dnd.created_on
            tmp["ll_type"] = dnd.type
            tmp["ll_orderid"] = dnd.order_id
            tmp["ll_amount"] = dnd.amount
        data.append(tmp)
    return data


def get_recondate():
    first = db.session.query(DebitNoteDate.date).filter(DebitNoteDate.state == False).order_by(
        DebitNoteDate.date.desc()).first()
    print first
    return first


def strit(item):
    return datetime.datetime.strftime(item, '%Y-%m-%d')


def datebyoff(days=0):
    return strit(datetime.datetime.now() - datetime.timedelta(days=days))


def download_sftp_bydate(date):
    date = date.replace("-", "")
    try:
        t = paramiko.Transport((config.Ftp.HOSTNAME, config.Ftp.PORT))
        t.connect(username=config.Ftp.USERNAME, password=config.Ftp.PASSWORD)

        sftp = paramiko.SFTPClient.from_transport(t)

        uri = config.Ftp.JYMX_PATH.format(oid_partner=config.OID_PARTNER, date=date)
        dst = "./%s.csv" % date
        sftp.get(uri, dst)
        t.close()
    except Exception as _:
        import traceback
        traceback.print_exc()
        try:
            t.close()
        except:
            pass


def create_DNDate(state, date, vas_name):
    dndate = DebitNoteDate(state=state, date=date, vas_name=vas_name)
    db.session.add(dndate)
    db.session.flush()


def create_DNDetail(sn, vas_name, amount, order_id, state, valid, created_on, type):
    first = db.session.query(DebitNoteDetail.sn).filter(DebitNoteDetail.sn == sn,
                                                        DebitNoteDetail.state == state).first()
    if not first:
        dndetail = DebitNoteDetail(sn=sn, vas_name=vas_name, amount=amount,
                                   order_id=order_id, state=state, valid=valid, created_on=created_on, type=type)
        db.session.add(dndetail)
        db.session.flush()


def get_begin_date():
    begin_date = datetime.datetime(2015, 8, 29)
    sql = """select date(`date`) from debit_note_date order by `date` desc limit 1 ;"""
    s = text(sql)
    result = db.session.execute(s).fetchone()
    if result:
        begin_date = result[0]
    tmpdate = begin_date + datetime.timedelta(days=1)
    tmpdate = strit(tmpdate)
    return tmpdate


def checkdate(date):
    sql = """select date(`date`) from debit_note_date where date="%s" order by `date` desc limit 1 ;""" % date
    s = text(sql)
    result = db.session.execute(s).fetchone()
    if result:
        return False

    sql = """select date(`date`) from debit_note_date order by `date` desc limit 1 ;"""
    s = text(sql)
    result = db.session.execute(s).fetchone()
    if result:
        tmpdate = result[0]
        if tmpdate > datetime.date.today():
            return False
        tmpdate += datetime.timedelta(days=1)
        if strit(tmpdate) == date:
            return True
    else:
        return True


# for mannage command
def main():
    begin_date = get_begin_date()
    print begin_date
    check_LL(begin_date)
    return begin_date


def init_recon():
    while True:
        begin_date = main()
        if begin_date == datebyoff(-1):
            break


def check_LL(date='2015-09-10'):
    if not checkdate(date):
        print "date is not valid"
        return

    lvyedata = lvyedata_ready(date)
    lldata = lldata_ready(date)
    lydata_bak = lvyedata[::]
    lldata_bak = lldata[::]

    print len(lydata_bak), len(lldata_bak)

    for n, ly in enumerate(lvyedata):
        for ll in lldata:
            if ly.sn == ll["sn"]:
                if ly.vas_name == ll["vas_name"]:
                    if float(ly.amount) == float(ll["amount"]):
                        if (ly.type == "PAYMENT" and ll["type"] == "0") or (ly.type == "REFUND" and ll["type"] == "5"):
                            lydata_bak[n] = None

    print len(lydata_bak), len(lldata_bak)

    for n, ll in enumerate(lldata):
        for ly in lvyedata:
            if ly.sn == ll["sn"]:
                if ly.vas_name == ll["vas_name"]:
                    if float(ly.amount) == float(ll["amount"]):
                        if (ly.type == "PAYMENT" and ll["type"] == "0") or (ly.type == "REFUND" and ll["type"] == "5"):
                            lldata_bak[n] = None

    lydata_bak = removeNone(lydata_bak)
    lldata_bak = removeNone(lldata_bak)
    print len(lydata_bak), len(lldata_bak)

    deletedata()
    lydata2db(lydata_bak)
    lldata2db(lldata_bak)

    create_DNDate(None, date=datetime.datetime.strptime(date, "%Y-%m-%d"), vas_name="LIANLIAN_PAY")

    date = date.replace("-", "")
    os.system("rm -f ./%s.csv" % date)


def removeNone(lst):
    result = []
    for item in lst:
        if item != None:
            result.append(item)
    return result


def lydata2db(lydata):
    for ly in lydata:
        print ly
        create_DNDetail(ly.sn, ly.vas_name, ly.amount, ly.order_id, state=ly.state, valid=ly.valid,
                        created_on=ly.created_on, type=ly.type)


def lldata2db(lldata):
    for ll in lldata:
        print ll
        create_DNDetail(ll["sn"], ll["vas_name"], ll["amount"], ll["vas_sn"], state=True, valid=False,
                        created_on=datetime.datetime.strptime(ll["created_on"], "%Y%m%d %H:%M:%S"),
                        type="PAYMENT" if ll["type"] == "0" else "REFUND")


def deletedata():
    sql = "delete from debit_note_detail;"
    print sql
    s = text(sql)
    db.session.execute(s)
    db.session.flush()


def lvyedata_ready(date='2015-09-10'):
    begin_date = get_begin_date()
    tmpdate = datetime.datetime.strptime(date, "%Y-%m-%d")
    tmpdate += datetime.timedelta(days=1)
    tmpdate = strit(tmpdate)
    sql = """select sa.vas_name,sa.amount,sa.created_on,tx_sn,t.type,t.state,t.order_id,t.type from system_asset_account_item sa left outer join event e on sa.event_id=e.id left outer join transaction t on e.tx_sn=t.sn where sa.vas_name='LIANLIAN_PAY' and t.type in ('PAYMENT','REFUND','PREPAID') and t.state in ('SUCCESS','REFUNDED','SECURED') and e.created_on < "%s" and e.created_on >= "%s" order by e.created_on ;""" % (
        tmpdate, begin_date)
    print sql

    s = text(sql)
    result = db.session.execute(s).fetchall()

    for ret in result:
        ttype = "PAYMENT" if ret.type == "PREPAID" else ret.type
        create_DNDetail(ret.tx_sn, ret.vas_name, ret.amount, ret.order_id, state=False, valid=False,
                        created_on=ret.created_on, type=ttype)

    ##clear same sn data
    clearsamesn()

    sql = """select * from debit_note_detail where valid=0; """
    s = text(sql)
    result = db.session.execute(s).fetchall()
    return list(result)


def clearsamesn():
    sql = """delete from debit_note_detail where sn in (select sn from (select sn,count(distinct(state)) as s from debit_note_detail group by sn,vas_name,amount,type) r where r.s=2); """
    s = text(sql)
    db.session.execute(s)
    db.session.flush()


def lldata_ready(date='2015-09-10'):
    download_sftp_bydate(date)
    return parse_file(date)


def init_run():
    for i in range(1, 100)[::-1]:
        print datebyoff(i)
        if datebyoff(i) < "2015-08-30": continue
        main(datebyoff(i))


def parse_file(date='2015-09-10'):
    date = date.replace("-", "")

    def cleanit(astr):
        return astr.strip().strip("=").strip("\"")

    result = []
    for line in open("./%s.csv" % date).readlines()[1:]:
        tmp = {}
        items = line.decode("gb18030").split(",")
        sn = cleanit(items[0])
        tmp['sn'] = sn
        tmp['vas_name'] = "LIANLIAN_PAY"
        tmp['amount'] = abs(float(cleanit(items[6])))
        tmp['type'] = cleanit(items[8])
        tmp['vas_sn'] = cleanit(items[4])
        tmp['created_on'] = cleanit(items[2])
        result.append(tmp)
    return result

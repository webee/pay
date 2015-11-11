# coding=utf-8
from flask import jsonify
from . import debitnote_mod as mod
from api_x.debit_note.sftp import getrecon,get_tx_by_orderid,get_tx_detail_by_txid
#from flask_json import  as_json_p


@mod.route('/getrecondata')
def getrecondata():
	data,date = getrecon()
	num = len(data)
	
	return jsonify(data=data,date=date,num=num)
	#return """alert({"num":1};);"""
@mod.route('/gettx/<orderid>')
def gettxbyorderid(orderid):
	tx = get_tx_by_orderid(orderid)
	return jsonify(tx = tx)
	

@mod.route('/gettxdetail/<txid>')
def gettxdetailbytxid(txid):
	txdetail,accountdata = get_tx_detail_by_txid(txid)
	return jsonify(txdetail = txdetail,ad=accountdata)

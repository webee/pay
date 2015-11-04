# coding=utf-8
from __future__ import unicode_literals


class WithdrawState:
    REQUESTED = "REQUESTED"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"


class PayToLvyeState:
    CREATED = "CREATED"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"


class RequestClientType:
    WEB = 'WEB'
    WAP = 'WAP'
    # IOS = 'IOS'
    # ANDROID = 'ANDROID'
    WEIXIN = 'WEIXIN'

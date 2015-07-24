# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import smtplib
from email.utils import parseaddr, formataddr
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from top_config import config
import json
import re
import textwrap
import logging

CHARSET_UTF8 = 'utf-8'
log = logging.getLogger(__name__)


def send_email(sender, recipients, subject, content_html, content_text=None, category=None):
    sender_name, sender_addr = parseaddr(sender)
    from_addr = formataddr((Header(sender_name, CHARSET_UTF8).encode(), sender_addr))

    msg = MIMEMultipart('alternative')
    msg['From'] = from_addr
    msg['Subject'] = subject

    smtp_api = SmtpApiHeader()
    smtp_api.addTo(recipients)
    if category:
        smtp_api.setCategory(category)
    smtp_api.addSubVal('-RECIPIENT_EMAIL-', recipients)

    msg["X-SMTPAPI"] = smtp_api.asJSON()

    part1 = MIMEText(content_html, 'html', CHARSET_UTF8)
    msg.attach(part1)
    if content_text:
        part2 = MIMEText(content_text, 'plain', CHARSET_UTF8)
        msg.attach(part2)
    cfg = config()
    username = cfg.get('email', 'username')
    password = cfg.get('email', 'password')
    log.info('Sending email to recipients: {}'.format(recipients))
    if cfg.get('app', 'prod') == 'true':
        s = smtplib.SMTP(cfg.get('email', 'sp_address'), port=cfg.get('email', 'sp_port'))
        s.login(username, password)
        s.sendmail(from_addr, cfg.get('email','sender_address'), msg.as_string())
        s.quit()
        log.info('email hand over to SENDGRID...')
    else:
        log.warning('NOT PRODUCT ENV, ignore sending email out')


def send_single_email(sender, recipient, subject, text, html=None, category=None):
    sender_name, sender_addr = parseaddr(sender)
    from_addr = formataddr((Header(sender_name, CHARSET_UTF8).encode(), sender_addr))
    recipient_name, recipient_addr = parseaddr(recipient)
    to_addr = formataddr((Header(recipient_name, CHARSET_UTF8).encode(), recipient_addr))

    msg = MIMEMultipart('alternative')
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject
    if category:
        msg["X-SMTPAPI"] = '{"category" : "%s"}' % category
    part1 = MIMEText(text, 'plain', CHARSET_UTF8)
    msg.attach(part1)
    if html:
        part2 = MIMEText(html, 'html', CHARSET_UTF8)
        msg.attach(part2)
    cfg = config()
    username = cfg.get('email', 'username')
    password = cfg.get('email', 'password')
    log.info('Sending email to recipient: {}'.format(recipient))
    s = smtplib.SMTP(cfg.get('email', 'sp_address'), port=cfg.get('email', 'sp_port'))
    s.login(username, password)
    s.sendmail(from_addr, to_addr, msg.as_string())
    s.quit()



class SmtpApiHeader:
    def __init__(self):
        self.data = {}

    def addTo(self, to):
        if not self.data.has_key('to'):
            self.data['to'] = []
        if type(to) is str:
            self.data['to'] += [to]
        else:
            self.data['to'] += to

    def addSubVal(self, var, val):
        if not self.data.has_key('sub'):
            self.data['sub'] = {}
        if type(val) is str:
            self.data['sub'][var] = [val]
        else:
            self.data['sub'][var] = val

    def setUniqueArgs(self, val):
        if type(val) is dict:
            self.data['unique_args'] = val

    def setCategory(self, cat):

        self.data['category'] = cat

    def addFilterSetting(self, fltr, setting, val):
        if not self.data.has_key('filters'):
            self.data['filters'] = {}
        if not self.data['filters'].has_key(fltr):
            self.data['filters'][fltr] = {}
        if not self.data['filters'][fltr].has_key('settings'):
            self.data['filters'][fltr]['settings'] = {}
        self.data['filters'][fltr]['settings'][setting] = val

    def asJSON(self):
        j = json.dumps(self.data)
        return re.compile('(["\]}])([,:])(["\[{])').sub('\1\2 \3', j)

    def as_string(self):
        j = self.asJSON()
        str = 'X-SMTPAPI: %s' % textwrap.fill(j, subsequent_indent='  ', width=72)
        return str


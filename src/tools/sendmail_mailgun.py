# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import requests
import json
from werkzeug.datastructures import MultiDict
import logging
from config import config

log = logging.getLogger(__name__)


MAIL_POST_URL = 'https://api.mailgun.net/v2/xinjingshijie.mailgun.org'
BATCH_SEND_TRUNK_SIZE = 10


def send_email(sender, recipients, subject, content_html, content_text=None, category=None):
    if content_text is None:
        import html2text
        content_text = html2text.html2text(content_html)

    # log.debug('sending to recipients: {}'.format(recipients))
    if config().get('app', 'prod') == 'true':
        requests.post(
            get_email_action_url('messages'),
            auth=('api', config().get('email','api_key')),
            data=MultiDict([('from', sender),
                            ('to', ','.join(recipients)),
                            ('subject', subject),
                            ('text', content_text),
                            ('html', content_html),
                            ('recipient-variables', as_recipient_variables(recipients)),
                            ('o:tag', category)])
        )
        # log.debug('{} email delivery request hand over to MAILGUN...'.format(len(recipients)))
    else:
        log.warning('NOT PRODUCT ENV, ignore sending email out')


def get_email_action_url(action):
    return '{}/{}'.format(MAIL_POST_URL, action)


def as_recipient_variables(recipients):
    recipient_variables = {}
    for recipient in recipients:
        recipient_variables[recipient] = {'email':recipient}
    return json.dumps(recipient_variables)


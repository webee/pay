# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging

log = logging.getLogger(__name__)
events = {}


def publish_event(event_name, **kwargs):
    handlers = events.get(event_name, [])

    for handler in handlers:
        handler(**kwargs)


def event(event_type): #syntax sugar
    def decorator(subscriber):
        register_event_handler(event_type, subscriber)
        return subscriber
    return decorator


def register_event_handler(event_name, func):
    log.info('EVENT_HANDLER_REGISTER: {}'.format(event_name))
    events.setdefault(event_name, []).append(func)


@event('new-world-coming-event')
def announce(message):
    print(message)

@event('new-world-coming-event')
def official_announce(message):
    print('we say: {}'.format(message))

if __name__ == '__main__':
    publish_event('new-world-coming-event', message='hello, there')


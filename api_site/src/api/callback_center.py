# -*- coding: utf-8 -*-
from api.util.enum import enum


class CallbackCenter(object):
    _CHANNEL_KEY_DIRECT = 'direct'
    _CHANNEL_KEY_SECURED = 'secured'

    def __init__(self):
        self._handlers = {}

    def bind_secured_handler(self, event, callback):
        self._handlers[event] = {CallbackCenter._CHANNEL_KEY_SECURED, callback}

    def bind_direct_handler(self, event, callback):
        self._handlers[event] = {CallbackCenter._CHANNEL_KEY_DIRECT, callback}

    def trigger(self, event, trade_id):
        if self._is_direct_payment(trade_id):
            return self._trigger(event, CallbackCenter._CHANNEL_KEY_DIRECT)
        if self._is_secured_payment(trade_id):
            return self._trigger(event, CallbackCenter._CHANNEL_KEY_SECURED)
        raise ValueError('Trade id [%s] is illegal value' % trade_id)

    def _trigger(self, event, channel):
        if not self._handlers.has_key(event):
            raise ValueError("There isn't any handler bound to event[%s]" % event)

        channel_handlers = self._handlers[event]
        if not channel_handlers.has_key(channel):
            raise ValueError("There isn't handler bound to event[{0}] and channel[{1}]".format(event, channel))

        return channel_handlers[channel]

    def _is_direct_payment(self, trade_id):
        return trade_id.startswith('DRP')

    def _is_secured_payment(self, trade_id):
        return trade_id.startswith('GTP')


event = enum(PAID='0', REDIRECT_WEB_AFTER_PAID='1')

callbacks = CallbackCenter()

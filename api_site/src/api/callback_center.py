# -*- coding: utf-8 -*-
import types
from pytoolbox.util.enum import enum, keyset_in_enum, value_in_enum


event = enum(PAY='0', PAID='1', REDIRECT_WEB_AFTER_PAID='2')


class CallbackCenter(object):
    _CHANNEL_KEY_DIRECT = 'direct'
    _CHANNEL_KEY_SECURED = 'secured'
    _EVENT_KEYSET = keyset_in_enum(event)

    def __init__(self):
        self._handlers = dict()
        self._latest_event = ''
        self._bind_default_event_handler(CallbackCenter._EVENT_KEYSET)

    def bind_secured_handler(self, _event, callback):
        if not self._handlers.has_key(_event):
            self._handlers[_event] = dict()
        self._handlers[_event][CallbackCenter._CHANNEL_KEY_SECURED] = callback

    def bind_direct_handler(self, _event, callback):
        if not self._handlers.has_key(_event):
            self._handlers[_event] = dict()
        self._handlers[_event][CallbackCenter._CHANNEL_KEY_DIRECT] = callback

    def trigger(self, _event, trade_id):
        if CallbackCenter._is_direct_payment(trade_id):
            return self._trigger(_event, CallbackCenter._CHANNEL_KEY_DIRECT)
        if CallbackCenter._is_secured_payment(trade_id):
            return self._trigger(_event, CallbackCenter._CHANNEL_KEY_SECURED)
        raise ValueError('Trade id [%s] is illegal value' % trade_id)

    def _trigger(self, _event, channel):
        if not self._handlers.has_key(_event):
            raise ValueError("There isn't any handler bound to event[%s]" % _event)

        channel_handlers = self._handlers[_event]
        if not channel_handlers.has_key(channel):
            raise ValueError("There isn't handler bound to event[{0}] and channel[{1}]".format(_event, channel))

        return channel_handlers[channel]

    @staticmethod
    def _is_direct_payment(trade_id):
        return trade_id.startswith('DRP')

    @staticmethod
    def _is_secured_payment(trade_id):
        return trade_id.startswith('GTP')

    def _add_method(self, method, name):
        self.__dict__[name] = types.MethodType(method, self.__class__)

    def _bind_default_event_handler(self, events):
        for _event_name in events:
            self._add_method(self._default_event_handler, _event_name.lower())

    @staticmethod
    def _filter_out_class_parameter(tuple_args):
        return [value for i, value in enumerate(tuple_args) if i > 0]

    def _default_event_handler(self, *args, **kwargs):
        if len(args) < 2:
            raise ValueError("There is no enough info to decide which handler should be called")
        args = CallbackCenter._filter_out_class_parameter(args)
        trade_id = args[0]
        return self.trigger(value_in_enum(event, self._latest_event), trade_id)(*args, **kwargs)

    @staticmethod
    def _is_supported_event(_event):
        return _event in CallbackCenter._EVENT_KEYSET

    def __getattribute__(self, item):
        item_in_upper_case = item.upper()
        if CallbackCenter._is_supported_event(item_in_upper_case):
            self._latest_event = item_in_upper_case
        return super(CallbackCenter, self).__getattribute__(item)


callbacks = CallbackCenter()

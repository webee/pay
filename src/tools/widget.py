# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import functools
import traceback
from markupsafe import Markup

widgets = {}


def widget(func):
    widget_name = func.__name__.replace('_widget', '')
    widget = Widget(widget_name, func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return widget.render(*args, **kwargs)

    register_widget(widget_name, wrapper)
    return wrapper


class Widget(object):
    def __init__(self, name, func):
        self.name = name
        self.func = func
        self.registered_by = str('\n').join(traceback.format_stack())

    def render(self, *args, **kwargs):
        content = self.func(*args, **kwargs)
        if content is None:
            return None
        return Markup(content)

    def __repr__(self):
        return 'widget {}'.format(self.name)


def register_widget(name, handler):
    if widgets.has_key(name):
        #raise Exception('Widget with name {} already registered! '.format(name))
        print('WARNING: Widget with name {} already registered! '.format(name))
    widgets[name] = handler


class WidgetLookup(object):
    def __getattr__(self, name):
        widget_handler = widgets.get(name, None)
        if not widget_handler:
            raise Exception('widget {} not found'.format(name))
        return widget_handler


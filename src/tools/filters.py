# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from widget import WidgetLookup


def datetime_filter(dt):
    if dt:
        return dt.strftime('%Y/%m/%d %H:%M:%S')
    else:
        return ''


def date_filter(dt):
    if dt:
        return dt.strftime('%Y/%m/%d')
    else:
        return ''

def checked_filter(bool_val):
    if bool_val:
        return 'checked'
    else:
        return ''


def register_filters(app):
    app.jinja_env.filters['datetime'] = datetime_filter
    app.jinja_env.filters['date'] = date_filter
    app.jinja_env.filters['checked'] = checked_filter

def register_global_functions(app):
    app.jinja_env.globals['widgets'] = WidgetLookup()

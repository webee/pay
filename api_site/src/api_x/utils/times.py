# -*- coding: utf-8 -*-
from datetime import datetime, tzinfo, timedelta


def datetime_to_str(timestamp):
    return timestamp.strftime('%Y%m%d%H%M%S')


def now_to_str():
    return datetime_to_str(datetime.now())


def time_offset(t, offset=0):
    d = timedelta(seconds=offset)
    return t + d


class TzName:
    GMT = 'GMT'
    EST = 'EST'


class Zone(tzinfo):
    def __init__(self, offset, is_dst, name):
        super(Zone, self).__init__()
        self.offset = offset
        self.is_dst = is_dst
        self.name = name

    def utcoffset(self, dt):
        return timedelta(hours=self.offset) + self.dst(dt)

    def dst(self, dt):
        return timedelta(hours=1) if self.is_dst else timedelta(0)

    def tzname(self, dt):
        return self.name


UTC = Zone(0, False, TzName.GMT)
GMT8 = Zone(8, False, TzName.GMT)


def utc2gmt8(t):
    t = t.replace(tzinfo=UTC)
    return t.astimezone(GMT8)


def utc2local(t, offset=8):
    t = t.replace(tzinfo=UTC)
    return t.astimezone(Zone(offset, False, TzName.GMT))


def today():
    td = datetime.today()
    return datetime(td.year, td.month, td.day)


def utctoday():
    td, n, un = datetime.today(), datetime.now(), datetime.utcnow()
    return datetime(td.year, td.month, td.day) - (n - un)
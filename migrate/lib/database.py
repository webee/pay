from __future__ import unicode_literals, print_function, division

import warnings
import logging

import psycopg2
from psycopg2.extensions import cursor as _cursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_READ_COMMITTED
from sqlalchemy.exc import SAWarning, SADeprecationWarning

from contextlib import contextmanager


psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

logger = logging.getLogger(__name__)

warnings.simplefilter('ignore', category=SAWarning)
warnings.simplefilter('ignore', category=SADeprecationWarning)

# host = config.get('database', 'host')
# dbname = config.get('database', 'dbname')
# user = config.get('database', 'user')
# password = config.get('database', 'password')
host = '127.0.0.1'
dbname = 'lvye_pay'
user = 'lvye_pay'
password = 'p@55word'

_conn = None

def _get_conn():
    global _conn
    _conn = psycopg2.connect(host=host, user=user, password=password, database=dbname)
    _conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

def get_conn():
    global _conn
    if _conn:
        try:
            cur = _conn.cursor()
            cur.execute('SELECT 1')
        except:
            logger.debug('Connection is invalid', exc_info=True)
            _get_conn()
        finally:
            pass
    else:
        _get_conn()
    return _conn

def release_conn(conn):
    pass

def get(query_string, parameters=None):
    """Returns the first row returned for the given query."""
    rows = _query(query_string, parameters)
    if not rows:
        return None
    elif len(rows) > 1:
        raise Exception("Multiple rows returned for database.get() query")
    else:
        return rows[0]

def scalar(query_string, parameters=None):
    """Returns the first column in the first row, return None if not found."""
    rows = _query(query_string, parameters)
    if not rows:
        return None
    else:
        return rows[0][0]

def batch(query_string, parameters=None, fetch_size=100, start=0):
    with transaction():
        cur = get_conn().cursor('cursor', cursor_factory=NamedTupleCursor)
        try:
            logger.debug(query_string + (' With parameter: ' + str(parameters) if parameters is not None else ''))
            cur.execute(query_string, parameters)
            records = cur.fetchmany(size=fetch_size)
            while len(records) > 0:
                yield records
                records = cur.fetchmany(size=fetch_size)
        finally:
            pass # server side cursor is implicitly closed at transaction end

def batch_execute(statements):
    with transaction():
        cur = get_conn().cursor()
        try:
            for query_string, parameters in statements:
                logger.debug(query_string + (' With parameter: ' + str(parameters) if parameters is not None else ''))
                cur.execute(query_string, parameters)
        finally:
            cur.close()

def execute(query_string, parameters=None):
    cur = get_conn().cursor()
    try:
        logger.debug(query_string + (' With parameter: ' + str(parameters) if parameters is not None else ''))
        cur.execute(query_string, parameters)
        return cur.rowcount
    finally:
        cur.close()

def insert(insert_string, parameters=None):
    cur = get_conn().cursor()
    try:
        logger.debug(insert_string + (' With parameter: ' + str(parameters) if parameters is not None else ''))
        cur.execute(insert_string + " RETURNING id", parameters)
        return cur.fetchone()[0]
    finally:
        cur.close()

def add(table, **kwargs):
    sql = 'INSERT INTO %s(%s) VALUES(%s)' % (table,
                                             ','.join(kwargs.keys()),
                                             ','.join(['%(' + key + ')s' for key in kwargs.keys()]))
    return insert(sql, kwargs)

def update(table_name, by, **values):
    where_clause = ' AND '.join(['{key}=%({param})s'.format(key=key, param=param) for key, param in by.keys()])

    sql = 'UPDATE %s SET %s%s' % (table_name,
                                             ','.join(['{key}=%({key})s'.format(key=key) for key in values.keys()]),
                                             ' WHERE %s' % where_clause if where_clause else '')

    return execute(sql, dict(by.conditions(), **values))

def delete(table_name, by):
    where_clause = ' AND '.join(['{key}=%({param})s'.format(key=key, param=param) for key, param in by.keys()])

    sql = 'DELETE FROM %s %s' % (table_name, ' WHERE %s' % where_clause if where_clause else '')

    return execute(sql, by.conditions())

def get_by(table_name, by=None, **kwargs):
    if by:
        where_clause = ' AND '.join(['{key}=%({param})s'.format(key=key, param=param) for key, param in by.keys()])
        conditions = by.conditions()
    else:
        where_clause = ' AND '.join(['{key}=%(by_{key})s'.format(key=key) for key in kwargs.keys()])
        conditions = dict([('by_'+key, param) for key, param in kwargs.items()])

    sql = 'SELECT * FROM %s %s' % (table_name, ' WHERE %s' % where_clause if where_clause else '')

    return get(sql, conditions)

def scalar_by(query_string, by):
    """scalar('id from audience_member', by(dict(email='test@abc.dom').items()))"""
    where_clause = ' AND '.join(['{key}=%({param})s'.format(key=key, param=param) for key, param in by.keys()])

    sql = 'SELECT %s %s' % (query_string, ' WHERE %s' % where_clause if where_clause else '')

    return scalar(sql, by.conditions())

@contextmanager
def transaction():
    conn = get_conn()
    conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
    try:
        yield None
    except:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

class NamedTupleCursor(_cursor):
    """Patched version of psycopg2.extras.NamedTupleCursor. Should be used until issues are fixed in official release."""

    def fetchone(self):
        t = _cursor.fetchone(self)
        if t is not None:
            nt = self._make_nt()
            return nt(*t)

    def fetchmany(self, size=None):
        ts = _cursor.fetchmany(self, size)
        nt = self._make_nt()
        return [nt(*t) for t in ts]

    def fetchall(self):
        ts = _cursor.fetchall(self)
        nt = self._make_nt()
        return [nt(*t) for t in ts]

    def __iter__(self):
        return iter(self.fetchall())

    try:
        from collections import namedtuple
    except ImportError, _exc:
        def _make_nt(self):
            raise self._exc
    else:
        def _make_nt(self, namedtuple=namedtuple):
            return namedtuple("Record", " ".join([d[0] for d in self.description]))

class by:
    def __init__(self, conditions):
        self._conditions = conditions

    def keys(self):
        return [(condition[0], 'by_'+condition[0]) for condition in self._conditions]

    def conditions(self):
        return dict([('by_'+condition[0], condition[1]) for condition in self._conditions])

def list(query_string, parameters=None):
    return _query(query_string, parameters)

def _query(query_string, parameters=None, cur_factory=NamedTupleCursor):
    logger.debug(query_string + (' With parameter: ' + str(parameters) if parameters is not None else ''))
    cur = get_conn().cursor(cursor_factory=cur_factory)
    try:
        cur.execute(query_string, parameters)
        return cur.fetchall()
    finally:
        cur.close()

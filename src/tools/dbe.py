from __future__ import unicode_literals, print_function, division

import os
from functools import wraps
from contextlib import contextmanager
import sqlalchemy
from sqlalchemy import create_engine
from mylog import get_logger
from pytoolbox.conf import config

LOGGER = get_logger(__name__, level=os.getenv('LOG_LEVEL', 'INFO'))


@contextmanager
def require_transaction_context():
    with engine.begin() as conn:
        yield DatabaseInterface(conn)


def transactional(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with require_transaction_context() as _:
            return func(*args, **kwargs)

    return wrapper


def db_transactional(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if '_db' in kwargs:
            db = kwargs.pop('_db')
            return func(db, *args, **kwargs)
        if len(args) > 1 and isinstance(args[0], DatabaseInterface):
            return func(*args, **kwargs)
        with require_transaction_context() as db:
            return func(db, *args, **kwargs)

    return wrapper


@contextmanager
def require_db_context():
    with engine.contextual_connect() as conn:
        yield DatabaseInterface(conn)


def db_context(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if '_db' in kwargs:
            db = kwargs.pop('_db')
            return func(db, *args, **kwargs)
        if len(args) > 1 and isinstance(args[0], DatabaseInterface):
            return func(*args, **kwargs)
        with require_db_context() as db:
            return func(db, *args, **kwargs)

    return wrapper


class DatabaseInterface(object):
    def __init__(self, conn=None):
        self.conn = conn

    def __eq__(self, other):
        if other is None or not isinstance(other, DatabaseInterface):
            return False
        return self.conn == other.conn

    def sleep(self, duration):
        sql = "select SLEEP(%s)"
        self._execute(sql, (duration,))

    def has_rows(self, sql, **kwargs):
        return self.get_scalar('SELECT EXISTS ({})'.format(sql), **kwargs)

    def _execute(self, *args, **kwargs):
        if self.conn is None:
            with engine.contextual_connect() as conn:
                return conn.execution_options(autocommit=True).execute(*args, **kwargs)
        else:
            return self.conn.execution_options(autocommit=True).execute(*args, **kwargs)

    def executemany(self, sql, seq_of_parameters):
        try:
            res = self._execute(sql, seq_of_parameters)
        except:
            LOGGER.exception(
                'failed to executemany statement: sql is %(sql)s and seq_of_parameters are %(seq_of_parameters)s', {
                    'sql': sql,
                    'seq_of_parameters': seq_of_parameters
                })
            raise
        return res.rowcount

    def execute(self, sql, *args, **kwargs):
        try:
            res = self._execute(sql, args or kwargs)
        except:
            LOGGER.exception('failed to execute statement: sql is %(sql)s and args are %(args)s', {
                'sql': sql,
                'args': args or kwargs
            })
            raise
        return res.rowcount

    def exists(self, sql, **kwargs):
        return self.get_scalar('SELECT EXISTS ({})'.format(sql), **kwargs)

    def list(self, sql, **kwargs):
        return self._query(sql, **kwargs)

    def list_scalar(self, sql, *args, **kwargs):
        rows = self._query(sql, *args, **kwargs)
        if rows and len(rows[0]) > 1:
            raise Exception('More than one columns returned: sql is %(sql)s and args are %(args)s', {
                'sql': sql,
                'args': args or kwargs
            })
        return [row[0] for row in rows]

    def get(self, sql, *args, **kwargs):
        rows = self._query(sql, *args, **kwargs)
        if not rows:
            LOGGER.debug('No rows returned: sql is %(sql)s and args are %(args)s', {
                'sql': sql,
                'args': args or kwargs
            })
            return None
        if len(rows) > 1:
            LOGGER.warning('More than one rows returned: sql is %(sql)s and args are %(args)s', {
                'sql': sql,
                'args': args or kwargs
            })
        return rows[0]

    def get_scalar(self, sql, *args, **kwargs):
        rows = self._query(sql, *args, **kwargs)
        if not rows:
            LOGGER.debug('No rows returned: sql is %(sql)s and args are %(args)s', {
                'sql': sql,
                'args': args or kwargs
            })
            return None
        if len(rows) > 1:
            LOGGER.warning('More than one rows returned: sql is %(sql)s and args are %(args)s', {
                'sql': sql,
                'args': args or kwargs
            })
        if len(rows[0]) > 1:
            raise Exception('More than one columns returned: sql is %(sql)s and args are %(args)s', {
                'sql': sql,
                'args': args or kwargs
            })
        return rows[0][0]

    def insert(self, table, values=None, returns_id=False, **value_fields):
        if values:
            if isinstance(values, list):
                column_names = values[0].keys()
                fields = [tuple(value[n] for n in column_names) for value in values]
            elif isinstance(values, dict):
                column_names = values.keys()
                fields = tuple(values[n] for n in column_names)
            else:
                raise ValueError("values should be list or dict, but get: {0}".format(type(values)))
        else:
            column_names = list(value_fields.keys())
            fields = tuple(value_fields[n] for n in column_names)

        fragments = ['INSERT INTO ', table,
                     ' (', ','.join(column_names), ' ) VALUES ',
                     '( ', ','.join(['%s'] * len(column_names)), ' )']
        sql = ''.join(fragments)

        try:
            res = self._execute(sql, fields)
        except:
            LOGGER.exception('failed to execute query: sql is %(sql)s and args are %(args)s', {
                'sql': sql,
                'args': fields
            })
            raise
        if returns_id:
            return res.lastrowid
        else:
            return res.rowcount

    def _query(self, sql, *args, **kwargs):
        try:
            res = self._execute(sql, args or kwargs)
        except:
            LOGGER.exception('failed to execute query: sql is %(sql)s and args are %(args)s', {
                'sql': sql,
                'args': args or kwargs
            })
            raise
        return res.fetchall()


def create_db_engine(**kwargs):
    db_host = config.get('database', 'host')
    db_port = config.get('database', 'port')
    db_instance = config.get('database', 'instance')
    username = config.get('database', 'user')
    password = config.get('database', 'password')
    url = sqlalchemy.engine.url.URL('mysql', username, password, db_host, db_port, db_instance, {'charset': 'utf8'})

    return create_engine(url, pool_size=30, max_overflow=60, pool_recycle=3600, pool_timeout=60, **kwargs)


engine = create_db_engine(strategy='threadlocal')


def from_db():
    return DatabaseInterface()

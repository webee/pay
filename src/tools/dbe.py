from __future__ import unicode_literals, print_function, division

import os
import inspect
from functools import wraps
from contextlib import contextmanager
import sqlalchemy
from sqlalchemy import create_engine
import file_config
from mylog import get_logger

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
        with require_transaction_context() as db:
            return func(db, *args, **kwargs)

    return wrapper


@contextmanager
def require_db_context():
    with engine.contextual_connect() as conn:
        yield DatabaseInterface(conn)


def db_operate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if '_db' in kwargs:
            db = kwargs.pop('_db')
            return func(db, *args, **kwargs)
        with require_db_context() as db:
            return func(db, *args, **kwargs)

    return wrapper


class DatabaseInterface(object):
    def __init__(self, conn, is_engine=False):
        self.conn = conn
        self.is_engine = is_engine

    @property
    def connection(self):
        if self.is_engine:
            raise AttributeError('this database is engine based.')
        return self.conn

    @property
    def engine(self):
        if not self.is_engine:
            raise AttributeError('this database is connection based.')
        return self.conn

    def sleep(self, duration):
        self.conn.execute("select SLEEP(%s)", (duration,))

    def has_rows(self, sql, **kwargs):
        return self.get_scalar('SELECT EXISTS ({})'.format(sql), **kwargs)

    def executemany(self, sql, seq_of_parameters):
        try:
            res = self.conn.execute(sql, seq_of_parameters)
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
            res = self.conn.execute(sql, args or kwargs)
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
            res = self.conn.execute(sql, fields)
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
            res = self.conn.execute(sql, args or kwargs)
        except:
            LOGGER.exception('failed to execute query: sql is %(sql)s and args are %(args)s', {
                'sql': sql,
                'args': args or kwargs
            })
            raise
        return res.fetchall()


class FunctionValueProvider(object):
    def __init__(self, func):
        self.func = func
        self.multiple_args = len(inspect.getargspec(func).args) > 1

    def __call__(self, obj):
        if self.multiple_args:
            return self.func(*obj)
        else:
            return self.func(obj)


class ConstValueProvider(object):
    def __init__(self, const):
        self.const = const

    def __call__(self, obj):
        return self.const


def create_db_engine(**kwargs):
    cfg = file_config.config()
    url = sqlalchemy.engine.url.URL('mysql',
                                    cfg.get('database', 'username'),
                                    cfg.get('database', 'password'),
                                    cfg.get('database', 'host'),
                                    int(cfg.get('database', 'port')) if cfg.get('database', 'port') else None,
                                    cfg.get('database', 'instance'),
                                    {'charset': 'utf8'}
                                    )

    return create_engine(url, pool_size=30, max_overflow=60, pool_recycle=3600, pool_timeout=60, **kwargs)


engine = create_db_engine(strategy='threadlocal')


def from_db():
    return DatabaseInterface(engine, is_engine=True)

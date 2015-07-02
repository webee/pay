from __future__ import unicode_literals, print_function, division
import logging
import inspect
from functools import wraps, partial
from contextlib import contextmanager, closing

import MySQLdb as mysql
import config
from tool.collection import *


LOGGER = logging.getLogger(__name__)


def transactional(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with require_transaction_context():
            return func(*args, **kwargs)

    return wrapper


@contextmanager
def require_transaction_context():
    db=from_db()
    if db.autocommit is False:
        yield
    else:
        db.disable_autocommit()
        try:
            yield
        except:
            try:
                raise
            finally:
                db.rollback_transaction()
        else:
            db.commit_transaction()
        finally:
            db.enable_autocommit()


class DatabaseInterface:
    def __init__(self, options):
        self.options = options

    @property
    def autocommit(self):
        return self.conn.autocommit

    @autocommit.setter
    def autocommit(self, on_off):
        self.conn.autocommit = on_off

    def disable_autocommit(self):
        if self.autocommit is not False:
            self.autocommit = False

    def enable_autocommit(self):
        if self.autocommit is not True:
            self.autocommit = True

    def rollback_transaction(self):
        try:
            self.conn.rollback()
        except:
            LOGGER.exception('Cannot rollback database transaction')

    def commit_transaction(self):
        try:
            self.conn.commit()
        except:
            LOGGER.exception('Cannot commit database transaction')
            raise

    def close(self):
        try:
            self.conn.close()
        except:
            LOGGER.exception('Cannot close database connection')

    def has_rows(self, sql, **kwargs):
        return self.get_scalar('SELECT EXISTS ({})'.format(sql), **kwargs)

    def executemany(self, sql, seq_of_parameters):
        with closing(self.conn.cursor(returns_dict_object=False)) as cursor:
            try:
                cursor.executemany(sql, seq_of_parameters)
            except Exception as e:
                LOGGER.exception(
                    'failed to executemany statement: sql is %(sql)s and seq_of_parameters are %(seq_of_parameters)s', {
                        'sql': sql,
                        'seq_of_parameters': seq_of_parameters
                    })
                raise
            return cursor.rowcount

    def execute(self, sql, **kwargs):
        return self._execute(sql, **kwargs)

    def connect(self):
        self.conn = mysql.connect(
            unix_socket=self.options.unix_socket,
            user=self.options.username,
            passwd=self.options.password,
            db=self.options.database,
            charset='utf8'
        )

    def _execute(self, sql, **kwargs):
        self.conn.ping(True)
        with closing(self.conn.cursor()) as cursor:
            try:
                cursor.execute(sql, kwargs)
            except Exception as e:
                LOGGER.exception('failed to execute statement: sql is %(sql)s and kwargs are %(kwargs)s', {
                    'sql': sql,
                    'kwargs': kwargs
                })
                raise
            return cursor.rowcount

    def has_rows(self, sql, **kwargs):
        return self.get_scalar('SELECT EXISTS ({})'.format(sql), **kwargs)

    def list(self, sql, **kwargs):
        return self._query(sql, **kwargs)

    def list_scalar(self, sql, **kwargs):
        rows = self._query(sql, **kwargs)
        if rows and len(rows[0]) > 1:
            raise Exception('More than one columns returned: sql is %(sql)s and kwargs are %(kwargs)s', {
                'sql': sql,
                'kwargs': kwargs
            })
        return [row[0] for row in rows]


    def get(self, sql, **kwargs):
        rows = self._query(sql, **kwargs)
        if not rows:
            LOGGER.debug('No rows returned: sql is %(sql)s and kwargs are %(kwargs)s', {
                'sql': sql,
                'kwargs': kwargs
            })
            return None
        if len(rows) > 1:
            LOGGER.warning('More than one rows returned: sql is %(sql)s and kwargs are %(kwargs)s', {
                'sql': sql,
                'kwargs': kwargs
            })
        return rows[0]

    def get_scalar(self, sql, **kwargs):
        rows = self._query(sql, **kwargs)
        if not rows:
            LOGGER.debug('No rows returned: sql is %(sql)s and kwargs are %(kwargs)s', {
                'sql': sql,
                'kwargs': kwargs
            })
            return None
        if len(rows) > 1:
            LOGGER.warning('More than one rows returned: sql is %(sql)s and kwargs are %(kwargs)s', {
                'sql': sql,
                'kwargs': kwargs
            })
        if len(rows[0]) > 1:
            raise Exception('More than one columns returned: sql is %(sql)s and kwargs are %(kwargs)s', {
                'sql': sql,
                'kwargs': kwargs
            })
        return rows[0].values()[0]

    def insert(self, table, objects=None, returns_id=False, should_insert=None, **value_providers):
        if objects is not None:
            if not objects:
                return None
        else:
            if not value_providers:
                return None
        column_names = list(value_providers.keys())

        def get_rows_values():
            if objects is not None:
                for column_name in column_names:
                    value_provider = value_providers[column_name]
                    if not inspect.isfunction(value_provider) and not isinstance(value_provider, partial):
                        value_providers[column_name] = ConstValueProvider(value_provider)
                    else:
                        value_providers[column_name] = FunctionValueProvider(value_provider)
                for object in objects:
                    if should_insert and not should_insert(object):
                        continue
                    yield [value_providers[column_name](object) for column_name in column_names]
            else:
                yield [value_providers[column_name] for column_name in column_names]

        fragments = ['INSERT INTO ', table, ' (']
        first = True
        arg_index = 0
        args = {}
        for column_name in column_names:
            if first:
                first = False
            else:
                fragments.append(', ')
            fragments.append(column_name)
        fragments.append(' ) VALUES ')
        first = True
        for row_values in get_rows_values():
            if first:
                first = False
            else:
                fragments.append(', ')
            first = True
            fragments.append('(')
            for cell_value in row_values:
                if first:
                    first = False
                else:
                    fragments.append(', ')
                arg_index += 1
                arg_name = ''.join(['a', unicode(arg_index)])
                fragments.append('%(')
                fragments.append(arg_name)
                fragments.append(')s')
                args[arg_name] = cell_value
            fragments.append(')')
        row_count = self.execute(''.join(fragments), **args)
        if returns_id:
            return self.get_scalar('SELECT LAST_INSERT_ID()')
        else:
            return row_count

    def _query(self, sql, **kwargs):
        self.conn.ping(True)
        with closing(self.conn.cursor()) as cursor:
            try:
                cursor.execute(sql, kwargs)
            except Exception as e:
                LOGGER.exception('failed to execute query: sql is %(sql)s and kwargs are %(kwargs)s', {
                    'sql': sql,
                    'kwargs': kwargs
                })
                raise

            def get_column_name( i):
                return cursor.description[i][0].lower()

            def to_dict_object(row):
                o = DictObject()
                for i, cell in enumerate(row):
                    o[get_column_name(i)] = cell
                return o

            return [to_dict_object(row) for row in cursor.fetchall()]


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


instance = []


def from_db():
    if len(instance) == 0:
        cfg = config.config()
        db = DatabaseInterface(objectify({
            'unix_socket': cfg.get('database', 'unix_socket'),
            'username': cfg.get('database', 'username'),
            'password': cfg.get('database', 'password'),
            'database': cfg.get('database', 'instance')

        }))
        db.connect()
        instance.append(db)
    return instance[0]

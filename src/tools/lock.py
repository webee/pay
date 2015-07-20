# coding=utf-8
from __future__ import unicode_literals
import contextlib
from .mylog import get_logger

logger = get_logger(__name__)


class LockError(Exception):
    def __init__(self, message):
        super(LockError, self).__init__(message)


class GetLockTimeoutError(LockError):
    def __init__(self, name, timeout):
        message = "get lock [{0}] timeout after {1} seconds.".format(name, timeout)
        super(GetLockTimeoutError, self).__init__(message)


class GetLockError(LockError):
    def __init__(self, name):
        message = "get lock [{0}] error.".format(name, )
        super(GetLockTimeoutError, self).__init__(message)


class CheckLockError(LockError):
    def __init__(self, name):
        message = "check lock [{0}] error.".format(name, )
        super(CheckLockError, self).__init__(message)


class _Locker(object):
    _id_locks = {
    }

    def __init__(self, db):
        self.db = db
        self.id = self.who_am_i()

    def sleep(self, duration):
        self.db.sleep(duration)

    def get_lock(self, name, timeout=-1):
        ret = self.db.get_scalar("select GET_LOCK(%s, %s)", (name, timeout))
        if ret == 0:
            raise GetLockTimeoutError(name, timeout)
        elif ret is None:
            raise GetLockError(name)

        _Locker._id_locks[self.id] = name

    def release_lock(self, name=None):
        name = _Locker._id_locks.get(self.id) or name
        ret = self.db.get_scalar("select RELEASE_LOCK(%s)", (name,))
        if ret == 0:
            logger.warn("lock [{0}] not established by this thread.".format(name, ))
        elif ret is None:
            logger.warn("lock [{0}] did not exists.".format(name, ))

        try:
            _Locker._id_locks.pop(self.id)
        except:
            pass

    def is_lock_free(self, name):
        ret = self.db.get_scalar("select IS_FREE_LOCK(%s)", (name,))
        if ret is None:
            raise CheckLockError(name)
        return True if ret == 1 else False

    def who_hold_the_lock(self, name):
        return self.db.get_scalar("select IS_USED_LOCK(%s)", (name,))

    def who_am_i(self):
        return self.db.get_scalar("select CONNECTION_ID()")

    def i_hold_the_lock(self, name):
        ret = self.db.get_scalar("select CONNECTION_ID() = IS_USED_LOCK(%s)", (name,))
        return True if ret == 1 else False

    @contextlib.contextmanager
    def lock(self, name, timeout=-1):
        if self.id in _Locker._id_locks:
            # already has a lock.
            lock_name = _Locker._id_locks[self.id]
            if lock_name != name:
                # try another lock
                raise LockError('already hold a lock: %s' % lock_name)
        if self.i_hold_the_lock(name):
            # nested the same lock.
            yield
        else:
            self.get_lock(name, timeout)

            try:
                yield
            except:
                raise
            finally:
                self.release_lock(name)

    @contextlib.contextmanager
    def user_account_lock(self, user_account_id, account_name, timeout=-1):
        with self.lock(_generate_user_lock_name(user_account_id, account_name), timeout):
            yield


def _generate_user_lock_name(user_account_id, name):
    return 'lvye_pay.{0}_{1}'.format(user_account_id, name)


@contextlib.contextmanager
def require_lock(name, timeout=-1):
    from .dbe import require_db_context
    with require_db_context() as db:
        locker = _Locker(db)
        with locker.lock(name, timeout):
            yield locker


@contextlib.contextmanager
def require_user_account_lock(user_account_id, account_name, timeout=-1):
    with require_lock(_generate_user_lock_name(user_account_id, account_name), timeout) as locker:
        yield locker


@contextlib.contextmanager
def require_user_lock(user_account_id, name, timeout=-1):
    with require_lock(_generate_user_lock_name(user_account_id, name), timeout) as locker:
        yield locker

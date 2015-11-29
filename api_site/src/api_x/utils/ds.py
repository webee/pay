# coding=utf-8
from __future__ import unicode_literals


class TypeValue(object):
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, TypeValue):
            return isinstance(other, TypeValue) and other.value == self.value
        return self.value == other

    def __hash__(self):
        return hash(self.value)

    def __setattr__(self, key, value):
        if key != 'value' or hasattr(self, key):
            raise TypeError("'TypeValue' object does not support value assignment")
        super(TypeValue, self).__setattr__(key, value)

    def __repr__(self):
        return "<TypeValue: %r>" % self.value

NULL_VALUE = TypeValue(None)


class Trie(object):
    def __init__(self, prefix=tuple(), entry_key='_', entry=NULL_VALUE, null_entry=None):
        self.prefix = prefix
        self.entry_key = entry_key
        self.null_entry = null_entry
        self.__root = {}
        if entry != NULL_VALUE:
            self.__root[self.entry_key] = entry

    @property
    def value(self):
        return self.__root.get(self.entry_key, NULL_VALUE)

    def put(self, path, entry):
        root = self.__root
        for p in path:
            if p not in root:
                root[p] = {}
            root = root[p]
        root[self.entry_key] = entry

    def __get_root(self, path=tuple):
        root = self.__root
        for p in path:
            if p not in root:
                raise KeyError('path: [{0}] not exists.'.format(path))
            root = root[p]
        return root

    def contains_path(self, path=tuple):
        try:
            _ = self.__get_root(path)
            return True
        except:
            return False

    def get(self, path=tuple()):
        root = self.__get_root(path)
        if self.entry_key not in root:
            raise Exception('path: [{0}] has no entry.'.format(path))
        return root[self.entry_key]

    def sub(self, path, *args):
        path = path if isinstance(path, (tuple, list)) else (path,) + args
        root = self.__get_root(path)
        prefix = self.prefix + path
        entry = root.get(self.entry_key, NULL_VALUE)
        sub = Trie(prefix=prefix, entry_key=self.entry_key, entry=entry, null_entry=self.null_entry)
        for path, entry in self.__walk(root, with_null=False):
            sub.put(path, entry)
        return sub

    def clone(self):
        return self.sub(tuple())

    def subs(self):
        """
        子trie
        :return:
        """
        root = self.__root
        for p in root:
            if p == self.entry_key:
                continue
            cur_root = root[p]
            prefix = self.prefix + (p,)
            entry = cur_root.get(self.entry_key, NULL_VALUE)
            sub = Trie(prefix=prefix, entry_key=self.entry_key, entry=entry, null_entry=self.null_entry)
            for path, entry in self.__walk(cur_root, with_null=False):
                sub.put(path, entry)
            yield sub

    def __walk(self, root, prev_path=tuple(), with_null=True, null_entry=NULL_VALUE):
        """ 遍历每一个path
        :param root:
        :param prev_path:
        :param with_null:
        :param null_entry:
        :return:
        """
        for p in root:
            if p == self.entry_key:
                continue

            cur_root = root[p]
            path = prev_path + (p,)
            if with_null or self.entry_key in cur_root:
                # NULL_VALUE用来判断是否设置了可选参数
                null_entry = self.null_entry if null_entry is NULL_VALUE else null_entry
                yield path, cur_root.get(self.entry_key, null_entry)
            for v in self.__walk(cur_root, path, with_null=with_null, null_entry=null_entry):
                yield v

    def walk(self, with_null=True, null_entry=NULL_VALUE):
        for v in self.__walk(self.__root, with_null=with_null, null_entry=null_entry):
            yield v

    def __iter__(self):
        for v in self.__walk(self.__root, with_null=False):
            yield v

    def get_default(self, path=tuple(), default=NULL_VALUE):
        try:
            return self.get(path)
        except:
            # NULL_VALUE用来判断是否设置了可选参数
            return self.null_entry if default is NULL_VALUE else default

    def __setitem__(self, path, entry):
        self.put(path, entry)

    def __getitem__(self, path):
        path = path if isinstance(path, (tuple, list)) else (path,)
        return self.get(path)

    def __contains__(self, path):
        try:
            _ = self.get(path)
        except:
            return False
        return True

    def __repr__(self):
        if self.value == NULL_VALUE:
            return '%r-> %r' % (self.prefix, [k for k in self.__root if k != self.entry_key])
        return '[%r: %r]-> %r' % (self.prefix, self.value, [k for k in self.__root if k != self.entry_key])

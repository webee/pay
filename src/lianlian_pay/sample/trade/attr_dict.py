# -*- coding: utf-8 -*-

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def merge_to(self, base_dict):
        cloned = base_dict.clone()
        cloned.__dict__.update(self.__dict__)
        return cloned

    def clone(self):
        cloned = AttrDict()
        cloned.__dict__ = self.__dict__.copy()
        return cloned

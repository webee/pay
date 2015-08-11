# -*- coding: utf-8 -*-

class HandledResult(object):
    def __init__(self, has_been_handled_by_3rd_party, is_successful=False):
        self.has_been_handled_by_3rd_party = has_been_handled_by_3rd_party
        self.is_successful = is_successful

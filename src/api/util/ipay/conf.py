# -*- coding: utf-8 -*-
from pytoolbox.conf import SectionReader, config as _config


class ZYTUrlReader(SectionReader):
    def __init__(self, config_obj, section_name):
        super(ZYTUrlReader, self).__init__(config_obj, section_name)

    def __getattr__(self, item):
        return super(ZYTUrlReader, self).__getattr__('url_' + item)


config = SectionReader(_config, 'lianlianpay')
zyt_url = ZYTUrlReader(_config, 'zyt')

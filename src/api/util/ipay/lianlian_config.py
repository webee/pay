# -*- coding: utf-8 -*-
import os
from api.util.attr_dict import AttrDict
from .configs import config, mock_config

configs = {
    'mock': mock_config.config,
    'default': config.config
}

config = configs[os.getenv('IPAY_CONFIG', 'default')]

# -*- coding: utf-8 -*-
import os
from .configs import config, mock_config, beta_config

configs = {
    'mock': mock_config.config,
    'beta': beta_config.config,
    'default': config.config
}

config = configs[os.getenv('IPAY_CONFIG', 'default')]

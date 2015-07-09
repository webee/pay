# coding=utf-8
from __future__ import unicode_literals, print_function
import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    """Base Common Configuration"""
    # system
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'base key.'
    PROPAGATE_EXCEPTIONS = True

    CONF_DIR = os.path.join(basedir, 'conf')
    HOST_URL = 'http://localhost'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class BetaConfig(Config):
    HOST_URL = 'http://newpay.lvye.info'


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


PAY_CONFIG = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'beta': BetaConfig,
    'production': ProductionConfig,

    'default': BetaConfig
}

PAY_API_CONFIG = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'beta': BetaConfig,
    'production': ProductionConfig,

    'default': BetaConfig
}

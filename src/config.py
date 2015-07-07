# coding=utf-8
from __future__ import unicode_literals, print_function
import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    """Base Common Configuration"""
    # system
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'base key.'
    PROPAGATE_EXCEPTIONS = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data/data-dev.sqlite')
    SQLALCHEMY_BINDS = {
    }


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data/data-dev.sqlite')
    SQLALCHEMY_BINDS = {
    }


class BetaConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('BETA_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data/data-dev.sqlite')
    SQLALCHEMY_BINDS = {
    }

    HOST_URL = 'http://newpay.lvye.info'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data/data.sqlite')
    SQLALCHEMY_BINDS = {
    }


PAY_CONFIG = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'beta': BetaConfig,
    'production': ProductionConfig,

    'default': BetaConfig
}

OP_CONFIG = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'beta': BetaConfig,
    'production': ProductionConfig,

    'default': BetaConfig
}

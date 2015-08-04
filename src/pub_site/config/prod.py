# coding=utf-8
from tools import pmc_config

DEBUG = False
TESTING = False

pmc_config.cover_inject_from_file(__name__, 'conf/t.yaml', path='prod')
pmc_config.cover_inject_from_file(__name__, 'conf/t.yaml', path='etc')

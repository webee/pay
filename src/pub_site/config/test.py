# coding=utf-8
from tools import pmc_config

TESTING = True

pmc_config.cover_inject_from_file(__name__, 'conf/t.yaml', names=['test'])

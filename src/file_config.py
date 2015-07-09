import os
import ConfigParser
import logging
from config import basedir

log = logging.getLogger(__name__)


def config():
    config_file = os.path.join(basedir, 'conf/site.config')

    cf = ConfigParser.ConfigParser()
    cf.read(config_file)
    return cf

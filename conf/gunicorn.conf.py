# coding=utf-8
import os
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

errorlog = os.path.join(basedir, 'logs/gunicorn-error.log')
accesslog = os.path.join(basedir, 'logs/gunicorn-access.log')
loglevel = 'warning'

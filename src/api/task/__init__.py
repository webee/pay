# coding=utf-8
import os
from celery import Celery


def make_celery_app(name):
    return Celery(name)

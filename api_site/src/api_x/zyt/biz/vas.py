# coding=utf-8
from __future__ import unicode_literals
from api_x import db
from .models import VirtualAccountSystem
from pytoolbox.util.dbs import transactional


@transactional
def add_vas(name):
    es = VirtualAccountSystem(name=name)
    db.session.add(es)

    return es


def get_vas_by_name(name):
    return VirtualAccountSystem.query.filter_by(name=name).first()

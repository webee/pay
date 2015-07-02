# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from op_site.domain.campaign import start_worker_loop
import logging


logging.basicConfig(format='[%(levelname)s]%(asctime)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.INFO)


def email_sender():
    start_worker_loop()

if __name__ == '__main__':
    import sys

    command = sys.argv[1]
    args = sys.argv[2:]
    module = __import__('worker')
    method = getattr(module, command)
    if args:
        method(args)
    else:
        method()


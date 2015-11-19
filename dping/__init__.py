# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import

import sys

from .ping import Ping


def ping():
    if len(sys.argv) != 2:
        print('Usage: sudo dping domain/ip')
        exit(1)
    Ping(sys.argv[1]).start()


if __name__ == '__main__':
    ping()

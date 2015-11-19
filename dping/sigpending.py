# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import

import contextlib

from ._sigpending import save_mask, pending_and_restore


@contextlib.contextmanager
def sigpending(*signos):
    save_mask(signos)
    yield
    pending_and_restore()

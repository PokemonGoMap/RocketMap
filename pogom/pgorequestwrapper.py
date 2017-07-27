#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

log = logging.getLogger(__name__)


class PGoRequestWrapper:
    def __init__(self, request):
        self.request = request

    def __getattr__(self, attr):
        log.info('PGoRequestWrapper getattr %s.', attr)
        orig_attr = self.request.__dict__[attr]

        if callable(orig_attr):
            def hooked(*args, **kwargs):
                result = orig_attr(*args, **kwargs)
                # Prevent wrapped class from becoming unwrapped.
                if result == self.request:
                    return self
                return result
            return hooked
        else:
            return orig_attr

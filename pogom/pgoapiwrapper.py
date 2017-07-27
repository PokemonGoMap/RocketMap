#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from .pgorequestwrapper import PGoRequestWrapper

log = logging.getLogger(__name__)


class PGoApiWrapper:
    def __init__(self, api):
        self.api = api

    def __getattr__(self, attr):
        log.info('PGoApiWrapper getattr %s.', attr)
        orig_attr = self.api.__getattribute__(attr)

        if callable(orig_attr):
            def hooked(*args, **kwargs):
                result = orig_attr(*args, **kwargs)
                return result
            return hooked
        else:
            return orig_attr

    def create_request(self, *args, **kwargs):
        request = self.api.create_request(*args, **kwargs)
        return PGoRequestWrapper(request)

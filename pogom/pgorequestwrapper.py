#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from .utils import get_args

log = logging.getLogger(__name__)


class PGoRequestWrapper:

    def __init__(self, request):
        log.debug('Wrapped PGoApiRequest.')
        args = get_args()

        self.request = request
        self.retries = args.api_retries

    def __getattr__(self, attr):
        orig_attr = getattr(self.request, attr)

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

    def do_call(self, retries_left, *args, **kwargs):
        try:
            log.debug('Sending API request. Retries left: %d.', retries_left)
            return self.request.call(*args, **kwargs)
        except:
            if retries_left > 0:
                log.debug('API request failed. Retrying...')
                return self.do_call(retries_left - 1, *args, **kwargs)
            else:
                raise

    def call(self, *args, **kwargs):
        # Retry x times on failure.
        return self.do_call(self.retries, *args, **kwargs)

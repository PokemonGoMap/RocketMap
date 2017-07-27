#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from .utils import get_async_requests_session

log = logging.getLogger(__name__)


class PGoRequestWrapper:

    def __init__(self, request):
        self.request = request

        # Get a session with auto-retries. Concurrency can stay at 1, we're
        # not re-using our session objects in other requests.
        api_retries = 3
        api_backoff_factor = 0.2
        api_concurrency = 1

        self.session = get_async_requests_session(
            api_retries,
            api_backoff_factor,
            api_concurrency)

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

    def call(self, *args, **kwargs):
        # Make sure request has retry session set w/ proxies.
        self.session.proxies = self.request.__parent__._session.proxies
        self.request.__parent__._session = self.session

        log.info('PGoRequestWrapper proxies: %s', self.session.proxies)

        result = self.request.call(*args, **kwargs)
        return result

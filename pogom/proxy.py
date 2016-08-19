#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import requests

from urlparse import urlparse

log = logging.getLogger(__name__)


# Simple function to do a https call to Niantic's system for testing proxy connectivity
def check_proxy(proxy):

    proxy_test_url = 'https://sso.pokemon.com/'
    proxy_url = urlparse(proxy)
    log.info('Checking proxy %s ...', proxy)
    try:
        proxy_response = requests.get(proxy_test_url, proxies={proxy_url.scheme: proxy_url.netloc})
        if proxy_response.status_code == 200:
            log.info('Proxy %s is ok', proxy)
            return proxy
        else:
            proxy_error = 'Wrong status code - ' + str(proxy_response.status_code)

    except Exception as e:
        proxy_error = e

    log.error('Unable to use proxy %s', proxy)
    log.error('Proxy error: %s', proxy_error)

    return False

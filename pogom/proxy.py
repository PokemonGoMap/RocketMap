#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import requests

log = logging.getLogger(__name__)


# Simple function to do a call to Niantic's system for testing proxy connectivity
def check_proxy(proxy):

    proxy_test_url = 'https://sso.pokemon.com/'

    log.debug('Checking proxy %s ...', proxy)

    try:
        proxy_response = requests.get(proxy_test_url, proxies={'http': proxy, 'https': proxy})

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

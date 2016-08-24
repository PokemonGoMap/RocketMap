#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import requests

log = logging.getLogger(__name__)


# Simple function to do a call to Niantic's system for testing proxy connectivity
def check_proxy(proxy_queue, timeout, proxies):

    proxy_test_url = 'https://sso.pokemon.com/'
    proxy = proxy_queue.get_nowait()

    log.debug('Checking proxy: %s', proxy[1])
    try:

        proxy_response = requests.get(proxy_test_url, proxies={'http': proxy[1], 'https': proxy[1]}, timeout=timeout)

        if proxy_response.status_code == 200:
            log.debug('Proxy %s is ok', proxy[1])
            proxy_queue.task_done()
            proxies.append(proxy[1])
            return True
        else:

            proxy_error = "Wrong status code - " + str(proxy_response.status_code)

    except requests.ConnectTimeout:
        proxy_error = "Connection timeout (" + str(timeout) + " second(s) ) via proxy " + proxy[1]

    except requests.ConnectionError:
        proxy_error = "Failed to connect to proxy " + proxy[1]

    log.error('%s', proxy_error)
    proxy_queue.task_done()

    return False

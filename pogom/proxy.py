#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import requests
import sys

from queue import Queue
from threading import Thread

log = logging.getLogger(__name__)


# Simple function to do a call to Niantic's system for testing proxy connectivity
def check_proxy(proxy_queue, timeout, proxies, show_warnings):

    proxy_test_url = 'https://sso.pokemon.com/'
    proxy = proxy_queue.get()

    if proxy and proxy[1]:

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

        except Exception as e:
            proxy_error = e

    else:
            proxy_error = "Empty proxy server"

    # Decrease output amount if there are lot of proxies
    if (show_warnings == True):
        log.warning('%s', proxy_error)
    else:
        log.debug('%s', proxy_error)
    proxy_queue.task_done()

    return False


# Check all proxies and return a working list with proxies
def check_proxies(args):

    #Load proxies from the file. Override args.proxy if specified
    if args.proxyfile is not None:
        log.info('Loading proxies from file.')

        if args.proxy is not None:
            del args.proxy[:]
        else:
            args.proxy = []

        with open(args.proxyfile) as f:
            for line in f:
                # Ignore blank lines and comment lines
                if len(line.strip()) == 0 or line.startswith('#'):
                    continue
                #print(line.strip())
                args.proxy.append(line.strip())

        log.info('Loaded %d proxies.', len(args.proxy))

	if len(args.proxy)==0:
            log.error('Proxy file was configured but no proxies were loaded! We are aborting!')
            sys.exit(1)
    #print(args.proxy)
 
    # No proxies - no cookies
    if (args.proxy is None) or (len(args.proxy)==0):
        log.info('No proxies are configured.')
        return None

    proxy_queue = Queue()
    total_proxies = len(args.proxy)
    
    log.info('Checking %d proxies...', total_proxies)
    if (total_proxies > 10):
        log.info('Enable "-d/--debug" to see checking details.')

    proxies = []

    for proxy in enumerate(args.proxy):
        proxy_queue.put(proxy)

        t = Thread(target=check_proxy,
                   name='check_proxy',
                   args=(proxy_queue, args.proxy_timeout, proxies, total_proxies <= 10))
        t.daemon = True
        t.start()

    # This is painfull but we need to wait here untill proxy_queue is completed so we have a working list of proxies
    proxy_queue.join()

    working_proxies = len(proxies)

    if working_proxies == 0:
        log.error('Proxy was configured but no working proxies were found! We are aborting!')
        sys.exit(1)
    else:
        log.info('Proxy check completed with %d working proxies of %d configured', working_proxies, total_proxies)
        return proxies

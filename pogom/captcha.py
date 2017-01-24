#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
 - Captcha Overseer:
   - Tracks incoming new captcha tokens
   - Monitors the captcha'd accounts queue
   - Launches captcha_solver threads
 - Captcha Solver Threads each:
   - Have a unique captcha token
   - Attempts to verifyChallenge
   - Puts account back in active queue
   - Pushes webhook messages with captcha status
'''

import logging
import math
import os
import sys
import traceback
import random
import time
import requests
import copy

from datetime import datetime, timedelta
from threading import Thread, Lock
from queue import Queue, Empty
from sets import Set

from pgoapi import PGoApi
from .fakePogoApi import FakePogoApi

from .models import Token
from .transform import jitter_location
from .account import check_login
from .proxy import get_new_proxy

log = logging.getLogger(__name__)


def captcha_overseer_thread(args, account_queue, captcha_queue, key_scheduler):
    solverId = 0
    captchaStatus = {}

    while True:
        # Run once every 15 seconds.
        sleep_timer = 15

        tokens_needed = captcha_queue.qsize()
        if tokens_needed > 0:
            tokens = Token.get_valid(tokens_needed)
            tokens_available = len(tokens)
            solvers = min(tokens_needed, tokens_available)
            log.info("Accounts on hold with captcha: %d - tokens available: %d",
                     tokens_needed, tokens_available)
            for i in range(0, solvers):
                captcha = captcha_queue.get()

                hash_key = None
                if args.hash_key:
                    hash_key = key_scheduler.next()

                captchaStatus[solverId] = {
                    'type': 'Solver',
                    'message': 'Creating captcha solving thread...',
                    'account': captcha['account'],
                    'location': captcha['last_step'],
                    'captcha_url': captcha['captcha_url'],
                    'token':  tokens[i],
                    'hash_key': hash_key
                }

                t = Thread(target=captcha_solving_thread,
                           name='captcha-solver-{}'.format(solverId),
                           args=(args, account_queue, captcha_queue,
                                 captchaStatus[solverId]))
                t.daemon = True
                t.start()

                captcha_queue.task_done()
                solverId += 1
                if solverId > 999:
                    solverId = 0
                # Wait a bit before launching next captcha-solver thread
                time.sleep(1)

            # Adjust captcha-overseer sleep timer
            sleep_timer -= 1 * solvers
        log.debug("Waiting %d seconds before next token query...", sleep_timer)
        time.sleep(sleep_timer)


def captcha_solving_thread(args, account_queue, captcha_queue, status):

    account = status['account']
    location = status['location']
    captcha_url = status['captcha_url']
    captcha_token = status['token']
    hash_key = status['hash_key']

    status['message'] = "Waking up account {} to verify captcha token.".format(
                         account['username'])
    log.info(status['message'])

    if args.mock != '':
        api = FakePogoApi(args.mock)
    else:
        api = PGoApi()

    if hash_key:
        log.debug("Using key {} for solving this captcha.".format(hash_key))
        api.activate_hash_server(hash_key)

    proxy_url = False
    if args.proxy:
        # Try to fetch a new proxy
        proxy_num, proxy_url = get_new_proxy(args)

        if proxy_url:
            log.debug("Using proxy %s", proxy_url)
            api.set_proxy({'http': proxy_url, 'https': proxy_url})

    # Jitter location up to 100 meters
    location = jitter_location(location, 100)
    api.set_position(*location)
    status['message'] = "Logging in..."
    check_login(args, account, api, location, proxy_url)

    response = api.verify_challenge(token=captcha_token)

    if 'success' in response['responses']['VERIFY_CHALLENGE']:
        status['message'] = (
            "Account {} successfully uncaptcha'd, returning to " +
            "active duty.").format(account['username'])
        log.info(status['message'])
        account_queue.put(account)
    else:
        status['message'] = (
            "Account {} failed verifyChallenge, putting back " +
            "in captcha queue.").format(account['username'])
        log.warning(status['message'])
        captcha_queue.put({'account': account,
                           'last_step': location,
                           'captcha_url': captcha_url})


# Return captcha_url if captcha is encountered
def check_captcha(response_dict):
    try:
        captcha_url = response_dict['responses'][
            'CHECK_CHALLENGE']['challenge_url']
        if len(captcha_url) > 1:
            return captcha_url
    except KeyError, e:
        log.error("Unable to check captcha: {}".format(e))

    return None


# Return True if captcha was succesfully solved
def automatic_captcha_solve(args, status, api, captcha_url, account,
                            account_failures, wh_queue):
    status['message'] = (
        "Account {} is encountering a captcha, starting 2captcha " +
        "sequence.").format(account['username'])
    log.warning(status['message'])

    captcha_token = token_request(args, status, captcha_url)
    if 'ERROR' in captcha_token:
        log.warning("Unable to resolve captcha, please check your " +
                    "2captcha API key and/or wallet balance.")
        account_failures.append({
            'account': account,
            'last_fail_time': now(),
            'reason': 'captcha failed to verify'})

        return False
    else:
        status['message'] = (
            "Retrieved captcha token, attempting to verify challenge" +
            " for {}.").format(account['username'])
        log.info(status['message'])

        response = api.verify_challenge(token=captcha_token)
        if 'success' in response['responses']['VERIFY_CHALLENGE']:
            status['message'] = "Account {} successfully uncaptcha'd.".format(
                account['username'])
            log.info(status['message'])

            return True
        else:
            status['message'] = (
                "Account {} failed verifyChallenge, putting away " +
                "account for now.").format(account['username'])
            log.info(status['message'])
            account_failures.append({
                'account': account,
                'last_fail_time': now(),
                'reason': 'captcha failed to verify'})

            return False


def token_request(args, status, url):
    s = requests.Session()
    # Fetch the CAPTCHA_ID from 2captcha.
    try:
        request_url = (
            "http://2captcha.com/in.php?key={}&method=userrecaptcha" +
            "&googlekey={}&pageurl={}").format(args.captcha_key,
                                               args.captcha_dsk, url)
        captcha_id = s.post(request_url).text.split('|')[1]
        captcha_id = str(captcha_id)
    # IndexError implies that the retuned response was a 2captcha error.
    except IndexError:
        return 'ERROR'
    status['message'] = (
        "Retrieved captcha ID: {}; now retrieving token.").format(captcha_id)
    log.info(status['message'])
    # Get the response, retry every 5 seconds if it's not ready.
    recaptcha_response = s.get(
        "http://2captcha.com/res.php?key={}&action=get&id={}".format(
            args.captcha_key, captcha_id)).text
    while 'CAPCHA_NOT_READY' in recaptcha_response:
        log.info("Captcha token is not ready, retrying in 5 seconds...")
        time.sleep(5)
        recaptcha_response = s.get(
            "http://2captcha.com/res.php?key={}&action=get&id={}".format(
                args.captcha_key, captcha_id)).text
    token = str(recaptcha_response.split('|')[1])
    return token

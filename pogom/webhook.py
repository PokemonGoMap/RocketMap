#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import requests
import time
from .utils import get_args
from threading import Thread
from queue import Queue
from datetime import datetime, timedelta

log = logging.getLogger(__name__)


def send_to_webhook(message_type, message):
    args = get_args()

    if not args.webhooks:
        # what are you even doing here...
        return

    data = {
        'type': message_type,
        'message': message
    }

    for w in args.webhooks:
        try:
            requests.post(w, json=data, timeout=(None, 1))
        except requests.exceptions.ReadTimeout:
            log.debug('Response timeout on webhook endpoint %s', w)
        except requests.exceptions.RequestException as e:
            log.debug(e)


def wh_overseer(args, whq):
    wh_unique_queue = Queue()
    unique_items = {}
    cleanup_time = int(round(time.time() * 1000)) + 300000

    for i in range(args.wh_threads):
        log.debug('Starting wh-updater worker thread %d', i)
        t = Thread(target=wh_updater, name='wh-updater-{}'.format(i), args=(args, wh_unique_queue))
        t.daemon = True
        t.start()
    log.info('master thread started')

    # The forever loop
    while True:
        try:
            # Loop the queue
            while True:
                whtype, message = whq.get()
                if whtype == 'pokemon':
                    pokemon_key = (message['encounter_id'], message['spawnpoint_id'])
                    if pokemon_key not in unique_items:
                        unique_items[pokemon_key] = message['disappear_time']
                        wh_unique_queue.put((whtype, message))
                elif whtype == 'pokestop':
                    pokestop_key = (message['pokestop_id'], message['last_modified_time'])
                    if pokestop_key not in unique_items:
                        unique_items[pokestop_key] = message['last_modified_time']
                        wh_unique_queue.put((whtype, message))
                elif whtype == 'gym':
                    gym_key = (message['gym_id'], message['last_modified'])
                    if gym_key not in unique_items:
                        unique_items[gym_key] = message['last_modified']
                        wh_unique_queue.put((whtype, message))
                else:
                    wh_unique_queue.put((whtype, message))

                whq.task_done()

                # delete expired keys every 5 minutes with 1 minute grace period
                if int(round(time.time() * 1000)) > cleanup_time:
                    cleanup_time = int(round(time.time() * 1000)) + 300000
                    unique_items = {k: v for k, v in unique_items.iteritems() if time.gmtime(v) > (datetime.utcnow() - timedelta(minutes=1)).timetuple()}

        except Exception as e:
            log.exception('Exception in wh_overseer: %s', e)


def wh_updater(args, q):
    # The forever loop
    while True:
        try:
            # Loop the queue
            while True:
                whtype, message = q.get()
                send_to_webhook(whtype, message)
                if q.qsize() > 50:
                    log.warning("Webhook queue is > 50 (@%d); try increasing --wh-threads", q.qsize())
                q.task_done()
        except Exception as e:
            log.exception('Exception in wh_updater: %s', e)

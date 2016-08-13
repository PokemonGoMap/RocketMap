#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Search Architecture:
 - Have a list of accounts
 - Create an "overseer" thread
 - Search Overseer:
   - Tracks incoming new location values
   - Tracks "paused state"
   - During pause or new location will clears current search queue
   - Starts search_worker threads
 - Search Worker Threads each:
   - Have a unique API login
   - Listens to the same Queue for areas to scan
   - Can re-login as needed
   - Shares a global lock for map parsing
'''

import logging
import time
import math
import LatLon

from threading import Thread, Lock
from queue import Queue, Empty

from pgoapi import PGoApi
from pgoapi.utilities import f2i
from pgoapi import utilities as util
from pgoapi.exceptions import AuthException

from .models import parse_map

log = logging.getLogger(__name__)

TIMESTAMP = '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'


def generate_location_steps(initial_loc, step_count):
    R = 6378137.0
    heartbeat = 70.0
    rings = 0

    # probably not correct and also not needed?
    # r_hex = 52.5

    # Convert the step limit of the worker into the r radius of the hexagon in meters?
    # Don't need to convert the step limit of the worker into the r radius of a hexagon.
    # Only the heartbeat is needed.
    # w_worker = (2 * steps - 1) * r_hex

    # 70 Meter diameter converted to gps scale
    d = 2.0 * heartbeat / 1000.0
    d_s = d
    brng_s = 0.0
    brng = 0.0

    # This calculates the degree the worker is facing when they move to their next location.
    mod = math.degrees(math.atan(1.732 / (6 * (step_count - 1) + 3)))

    # Shouldn't need to calculate the number of workers because its no longer being used in the for loop.
    # total_workers = (((rings * (rings - 1)) *3) + 1)

    # This initialises the list.
    locations = [LatLon.LatLon(LatLon.Latitude(0), LatLon.Longitude(0))]

    # This sets the initial location for worker 0.
    locations[0] = LatLon.LatLon(LatLon.Latitude(initial_loc[0]), LatLon.Longitude(initial_loc[1]))

    # Insert initial location in search locations.
    yield (initial_loc[0], initial_loc[1], 0)

    turns = 0               # number of turns made in this ring (0 to 6)
    turn_steps = 0          # number of cells required to complete one turn of the ring
    turn_steps_so_far = 0   # current cell number in this side of the current ring

    while rings < step_count:
        for i in range(rings):
            if turns == 6 or turn_steps == 0:
                # we have completed a ring (or are starting the very first ring)
                turns = 0
                turn_steps += 1
                turn_steps_so_far = 0
                rings += 1

            if turn_steps_so_far == 0:
                brng = brng_s
                loc = locations[0]
                d = turn_steps * d
            else:
                loc = locations[0]
                C = math.radians(60.0)  # inside angle of a regular hexagon.
                a = d_s / R * 2.0 * math.pi  # in radians get the arclength of the unit circle covered by d_s.
                b = turn_steps_so_far * d_s / turn_steps / R * 2.0 * math.pi
                # The first spherical law of cosines gives us the length of side c from known angle C.
                c = math.acos(math.cos(a) * math.cos(b) + math.sin(a) * math.sin(b) * math.cos(C))
                # Turnsteps here represents ring number because yay coincidence always the same.
                # Multiply by derived arclength and convert to meters.
                d = turn_steps * c * R / 2.0 / math.pi
                # From the first spherical law of cosines we get the angle A from the side lengths a b c.
                A = math.acos((math.cos(b) - math.cos(a) * math.cos(c)) / (math.sin(c) * math.sin(a)))
                brng = 60 * turns + math.degrees(A)

            # This offsets the LatLon location using the bearing + mod as the direction, travelling the length of d.
            loc = loc.offset(brng + mod, d)
            locations.append(loc)  # This appends the location to the locations list.
            d = d_s
            turn_steps_so_far += 1
            if turn_steps_so_far >= turn_steps:
                # make a turn
                brng_s += 60.0
                brng = brng_s
                turns += 1
                turn_steps_so_far = 0
            yield (float(loc.to_string()[0]), float(loc.to_string()[1]), 0)  # Insert steps in search locations.


#
# A fake search loop which does....nothing!
#
def fake_search_loop():
    while True:
        log.info('Fake search loop running')
        time.sleep(10)


# The main search loop that keeps an eye on the over all process
def search_overseer_thread(args, new_location_queue, pause_bit, encryption_lib_path):

    log.info('Search overseer starting')

    search_items_queue = Queue()
    parse_lock = Lock()

    # Create a search_worker_thread per account
    log.info('Starting search worker threads')
    for i, account in enumerate(args.accounts):
        log.debug('Starting search worker thread %d for user %s', i, account['username'])
        t = Thread(target=search_worker_thread,
                   name='search_worker_{}'.format(i),
                   args=(args, account, search_items_queue, parse_lock,
                         encryption_lib_path))
        t.daemon = True
        t.start()

    # A place to track the current location
    current_location = False

    # The real work starts here but will halt on pause_bit.set()
    while True:

        # paused; clear queue if needed, otherwise sleep and loop
        if pause_bit.is_set():
            if not search_items_queue.empty():
                try:
                    while True:
                        search_items_queue.get_nowait()
                except Empty:
                    pass
            time.sleep(1)
            continue

        # If a new location has been passed to us, get the most recent one
        if not new_location_queue.empty():
            log.info('New location caught, moving search grid')
            try:
                while True:
                    current_location = new_location_queue.get_nowait()
            except Empty:
                pass

            # We (may) need to clear the search_items_queue
            if not search_items_queue.empty():
                try:
                    while True:
                        search_items_queue.get_nowait()
                except Empty:
                    pass

        # If there are no search_items_queue either the loop has finished (or been
        # cleared above) -- either way, time to fill it back up
        if search_items_queue.empty():
            log.debug('Search queue empty, restarting loop')
            for step, step_location in enumerate(generate_location_steps(current_location, args.step_limit), 1):
                log.debug('Queueing step %d @ %f/%f/%f', step, step_location[0], step_location[1], step_location[2])
                search_args = (step, step_location)
                search_items_queue.put(search_args)
        # else:
        #     log.info('Search queue processing, %d items left', search_items_queue.qsize())

        # Now we just give a little pause here
        time.sleep(1)


def search_worker_thread(args, account, search_items_queue, parse_lock, encryption_lib_path):

    # If we have more than one account, stagger the logins such that they occur evenly over scan_delay
    if len(args.accounts) > 1:
        delay = (args.scan_delay / len(args.accounts)) * args.accounts.index(account)
        log.debug('Delaying thread startup for %.2f seconds', delay)
        time.sleep(delay)

    log.debug('Search worker thread starting')

    # The forever loop for the thread
    while True:
        try:
            log.debug('Entering search loop')

            # Create the API instance this will use
            api = PGoApi()
            if args.proxy:
                api.set_proxy({'http': args.proxy, 'https': args.proxy})

            # Get current time
            loop_start_time = int(round(time.time() * 1000))

            # The forever loop for the searches
            while True:

                # Grab the next thing to search (when available)
                step, step_location = search_items_queue.get()

                log.info('Search step %d beginning (queue size is %d)', step, search_items_queue.qsize())

                # Let the api know where we intend to be for this loop
                api.set_position(*step_location)

                # The loop to try very hard to scan this step
                failed_total = 0
                while True:

                    # After so many attempts, let's get out of here
                    if failed_total >= args.scan_retries:
                        # I am choosing to NOT place this item back in the queue
                        # otherwise we could get a "bad scan" area and be stuck
                        # on this overall loop forever. Better to lose one cell
                        # than have the scanner, essentially, halt.
                        log.error('Search step %d went over max scan_retires; abandoning', step)
                        break

                    # Increase sleep delay between each failed scan
                    # By default scan_dela=5, scan_retries=5 so
                    # We'd see timeouts of 5, 10, 15, 20, 25
                    sleep_time = args.scan_delay * (1 + failed_total)

                    # Ok, let's get started -- check our login status
                    check_login(args, account, api, step_location)

                    api.activate_signature(encryption_lib_path)

                    # Make the actual request (finally!)
                    response_dict = map_request(api, step_location)

                    # G'damnit, nothing back. Mark it up, sleep, carry on
                    if not response_dict:
                        log.error('Search step %d area download failed, retrying request in %g seconds', step, sleep_time)
                        failed_total += 1
                        time.sleep(sleep_time)
                        continue

                    # Got the response, lock for parsing and do so (or fail, whatever)
                    with parse_lock:
                        try:
                            parse_map(response_dict, step_location)
                            log.debug('Search step %s completed', step)
                            search_items_queue.task_done()
                            break  # All done, get out of the request-retry loop
                        except KeyError:
                            log.exception('Search step %s map parsing failed, retrying request in %g seconds. Username: %s', step, sleep_time, account['username'])
                            failed_total += 1
                            time.sleep(sleep_time)

                # If there's any time left between the start time and the time when we should be kicking off the next
                # loop, hang out until its up.
                sleep_delay_remaining = loop_start_time + (args.scan_delay * 1000) - int(round(time.time() * 1000))
                if sleep_delay_remaining > 0:
                    time.sleep(sleep_delay_remaining / 1000)

                loop_start_time += args.scan_delay * 1000

        # catch any process exceptions, log them, and continue the thread
        except Exception as e:
            log.exception('Exception in search_worker: %s. Username: %s', e, account['username'])


def check_login(args, account, api, position):

    # Logged in? Enough time left? Cool!
    if api._auth_provider and api._auth_provider._ticket_expire:
        remaining_time = api._auth_provider._ticket_expire / 1000 - time.time()
        if remaining_time > 60:
            log.debug('Credentials remain valid for another %f seconds', remaining_time)
            return

    # Try to login (a few times, but don't get stuck here)
    i = 0
    api.set_position(position[0], position[1], position[2])
    while i < args.login_retries:
        try:
            api.set_authentication(provider=account['auth_service'], username=account['username'], password=account['password'])
            break
        except AuthException:
            if i >= args.login_retries:
                raise TooManyLoginAttempts('Exceeded login attempts')
            else:
                i += 1
                log.error('Failed to login to Pokemon Go with account %s. Trying again in %g seconds', account['username'], args.login_delay)
                time.sleep(args.login_delay)

    log.debug('Login for account %s successful', account['username'])


def map_request(api, position):
    try:
        cell_ids = util.get_cell_ids(position[0], position[1])
        timestamps = [0, ] * len(cell_ids)
        return api.get_map_objects(latitude=f2i(position[0]),
                                   longitude=f2i(position[1]),
                                   since_timestamp_ms=timestamps,
                                   cell_id=cell_ids)
    except Exception as e:
        log.warning('Exception while downloading map: %s', e)
        return False


class TooManyLoginAttempts(Exception):
    pass

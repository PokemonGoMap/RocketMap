#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Schedulers determine how worker's queues get filled. They control which locations get scanned,
in what order, at what time. This allows further optimizations to be easily added, without
having to modify the existing overseer and worker thread code.

Schedulers will recieve:

queues - A list of queues for the workers they control. For now, this is a list containing a
            single queue.
status - A list of status dicts for the workers. Schedulers can use this information to make
            more intelligent scheduling decisions. Useful values include:
            - last_scan_time: unix timestamp of when the last scan was completed
            - location: [lat,lng,alt] of the last scan
args - The configuration arguments. This may not include all of the arguments, just ones that are
            relevant to this scheduler instance (eg. if multiple locations become supported, the args
            passed to the scheduler will only contain the parameters for the location it handles)

Schedulers must fill the queues with items to search.

Queue items are a list containing:
    [step, (latitude, longitude, altitude), scan_seconds, disappears_seconds)]
Where:
    - step is the step number. Used only for display purposes.
    - (latitude, longitude, altitude) is the location to be scanned.
    - scan_seconds is the unix timestamp of when the search worker should scan
    - disappears_seconds is the unix timestamp of when the pokemon next disappears

    scan_seconds and disappears_seconds are used to skip scans that are too late, and wait for scans the
    worker is early for.  If a scheduler doesn't have a specific time a location needs to be scanned, it
    should set both to 0.

If implementing a new scheduler, place it before SchedulerFactory, and add it to __scheduler_classes
'''

import logging
import math
import geopy
import json
from queue import Empty
from operator import itemgetter
from .transform import get_new_coords
from .models import hex_bounds, Pokemon
from .utils import now, cur_sec

log = logging.getLogger(__name__)


# Simple base class that all other schedulers inherit from
# Most of these functions should be overridden in the actual scheduler classes.
# Not all scheduler methods will need to use all of the functions.
class BaseScheduler(object):
    def __init__(self, queues, status, args):
        self.queues = queues
        self.status = status
        self.args = args
        self.scan_location = False
        self.size = None

    # schedule function fills the queues with data
    def schedule(self):
        log.warning('BaseScheduler does not schedule any items')

    # location_changed function is called whenever the location being scanned changes
    # scan_location = (lat, lng, alt)
    def location_changed(self, scan_location):
        self.scan_location = scan_location
        self.empty_queues()

    # scanning_pause function is called when scanning is paused from the UI
    # The default function will empty all the queues.
    # Note: This function is called repeatedly while scanning is paused!
    def scanning_paused(self):
        self.empty_queues()

    def getsize(self):
        return self.size

    # Function to empty all queues in the queues list
    def empty_queues(self):
        for queue in self.queues:
            if not queue.empty():
                try:
                    while True:
                        queue.get_nowait()
                except Empty:
                    pass


# Hex Search is the classic search method, with the pokepath modification, searching in a hex grid around the center location
class HexSearch(BaseScheduler):

    # Call base initialization, set step_distance
    def __init__(self, queues, status, args):
        BaseScheduler.__init__(self, queues, status, args)

        # If we are only scanning for pokestops/gyms, the scan radius can be 900m.  Otherwise 70m
        if self.args.no_pokemon:
            self.step_distance = 0.900
        else:
            self.step_distance = 0.070

        self.step_limit = args.step_limit

        # This will hold the list of locations to scan so it can be reused, instead of recalculating on each loop
        self.locations = False

    # On location change, empty the current queue and the locations list
    def location_changed(self, scan_location):
        self.scan_location = scan_location
        self.empty_queues()
        self.locations = False

    # Generates the list of locations to scan
    def _generate_locations(self):
        NORTH = 0
        EAST = 90
        SOUTH = 180
        WEST = 270

        xdist = math.sqrt(3) * self.step_distance  # dist between column centers
        ydist = 3 * (self.step_distance / 2)       # dist between row centers

        results = []

        results.append((self.scan_location[0], self.scan_location[1], 0))

        if self.step_limit > 1:
            loc = self.scan_location

            # upper part
            ring = 1
            while ring < self.step_limit:

                loc = get_new_coords(loc, xdist, WEST if ring % 2 == 1 else EAST)
                results.append((loc[0], loc[1], 0))

                for i in range(ring):
                    loc = get_new_coords(loc, ydist, NORTH)
                    loc = get_new_coords(loc, xdist / 2, EAST if ring % 2 == 1 else WEST)
                    results.append((loc[0], loc[1], 0))

                for i in range(ring):
                    loc = get_new_coords(loc, xdist, EAST if ring % 2 == 1 else WEST)
                    results.append((loc[0], loc[1], 0))

                for i in range(ring):
                    loc = get_new_coords(loc, ydist, SOUTH)
                    loc = get_new_coords(loc, xdist / 2, EAST if ring % 2 == 1 else WEST)
                    results.append((loc[0], loc[1], 0))

                ring += 1

            # lower part
            ring = self.step_limit - 1

            loc = get_new_coords(loc, ydist, SOUTH)
            loc = get_new_coords(loc, xdist / 2, WEST if ring % 2 == 1 else EAST)
            results.append((loc[0], loc[1], 0))

            while ring > 0:

                if ring == 1:
                    loc = get_new_coords(loc, xdist, WEST)
                    results.append((loc[0], loc[1], 0))

                else:
                    for i in range(ring - 1):
                        loc = get_new_coords(loc, ydist, SOUTH)
                        loc = get_new_coords(loc, xdist / 2, WEST if ring % 2 == 1 else EAST)
                        results.append((loc[0], loc[1], 0))

                    for i in range(ring):
                        loc = get_new_coords(loc, xdist, WEST if ring % 2 == 1 else EAST)
                        results.append((loc[0], loc[1], 0))

                    for i in range(ring - 1):
                        loc = get_new_coords(loc, ydist, NORTH)
                        loc = get_new_coords(loc, xdist / 2, WEST if ring % 2 == 1 else EAST)
                        results.append((loc[0], loc[1], 0))

                    loc = get_new_coords(loc, xdist, EAST if ring % 2 == 1 else WEST)
                    results.append((loc[0], loc[1], 0))

                ring -= 1

        # This will pull the last few steps back to the front of the list
        # so you get a "center nugget" at the beginning of the scan, instead
        # of the entire nothern area before the scan spots 70m to the south.
        if self.step_limit >= 3:
            if self.step_limit == 3:
                results = results[-2:] + results[:-2]
            else:
                results = results[-7:] + results[:-7]

        # Add the required appear and disappear times
        locationsZeroed = []
        for step, location in enumerate(results, 1):
            locationsZeroed.append((step, (location[0], location[1], 40.32), 0, 0))
        return locationsZeroed

    # Schedule the work to be done
    def schedule(self):
        if not self.scan_location:
            log.warning('Cannot schedule work until scan location has been set')
            return

        # Only generate the list of locations if we don't have it already calculated.
        if not self.locations:
            self.locations = self._generate_locations()

        for location in self.locations:
            # FUTURE IMPROVEMENT - For now, queues is assumed to have a single queue.
            self.queues[0].put(location)
            log.debug("Added location {}".format(location))
        self.size = len(self.locations)


# Spawn Only Hex Search works like Hex Search, but skips locations that have no known spawnpoints
class HexSearchSpawnpoint(HexSearch):

    def _any_spawnpoints_in_range(self, coords, spawnpoints):
        return any(geopy.distance.distance(coords, x).meters <= 70 for x in spawnpoints)

    # Extend the generate_locations function to remove locations with no spawnpoints
    def _generate_locations(self):
        n, e, s, w = hex_bounds(self.scan_location, self.step_limit)
        spawnpoints = set((d['latitude'], d['longitude']) for d in Pokemon.get_spawnpoints(s, w, n, e))

        if len(spawnpoints) == 0:
            log.warning('No spawnpoints found in the specified area!  (Did you forget to run a normal scan in this area first?)')

        # Call the original _generate_locations
        locations = super(HexSearchSpawnpoint, self)._generate_locations()

        # Remove items with no spawnpoints in range
        locations = [coords for coords in locations if self._any_spawnpoints_in_range(coords[1], spawnpoints)]
        return locations


# Spawn Scan searches known spawnpoints at the specific time they spawn.
class SpawnScan(BaseScheduler):
    def __init__(self, queues, status, args):
        BaseScheduler.__init__(self, queues, status, args)
        # On the first scan, we want to search the last 15 minutes worth of spawns to get existing
        # pokemon onto the map.
        self.firstscan = True

        # If we are only scanning for pokestops/gyms, the scan radius can be 900m.  Otherwise 70m
        if self.args.no_pokemon:
            self.step_distance = 0.900
        else:
            self.step_distance = 0.070

        self.step_limit = args.step_limit
        self.locations = False

    # Generate locations is called when the locations list is cleared - the first time it scans or after a location change.
    def _generate_locations(self):
        # Attempt to load spawns from file
        if self.args.spawnpoint_scanning != 'nofile':
            log.debug('Loading spawn points from json file @ %s', self.args.spawnpoint_scanning)
            try:
                with open(self.args.spawnpoint_scanning) as file:
                    self.locations = json.load(file)
            except ValueError as e:
                log.exception(e)
                log.error('JSON error: %s; will fallback to database', e)
            except IOError as e:
                log.error('Error opening json file: %s; will fallback to database', e)

        # No locations yet? Try the database!
        if not self.locations:
            log.debug('Loading spawn points from database')
            self.locations = Pokemon.get_spawnpoints_in_hex(self.scan_location, self.args.step_limit)

        # Well shit...
        # if not self.locations:
        #    raise Exception('No availabe spawn points!')

        # locations[]:
        # {"lat": 37.53079079414139, "lng": -122.28811690874117, "spawnpoint_id": "808f9f1601d", "time": 511

        log.info('Total of %d spawns to track', len(self.locations))

        # locations.sort(key=itemgetter('time'))

        if self.args.very_verbose:
            for i in self.locations:
                sec = i['time'] % 60
                minute = (i['time'] / 60) % 60
                m = 'Scan [{:02}:{:02}] ({}) @ {},{}'.format(minute, sec, i['time'], i['lat'], i['lng'])
                log.debug(m)

        # 'time' from json and db alike has been munged to appearance time as seconds after the hour
        # Here we'll convert that to a real timestamp
        for location in self.locations:
            # For a scan which should cover all CURRENT pokemon, we can offset
            # the comparison time by 15 minutes so that the "appears" time
            # won't be rolled over to the next hour.

            # TODO: Make it work. The original logic (commented out) was producing
            #       bogus results if your first scan was in the last 15 minute of
            #       the hour. Wrapping my head around this isn't work right now,
            #       so I'll just drop the feature for the time being. It does need
            #       to come back so that repositioning/pausing works more nicely,
            #       but we can live without it too.

            # if sps_scan_current:
            #     cursec = (location['time'] + 900) % 3600
            # else:
            cursec = location['time']

            if cursec > cur_sec():
                # hasn't spawn in the current hour
                from_now = location['time'] - cur_sec()
                appears = now() + from_now
            else:
                # won't spawn till next hour
                late_by = cur_sec() - location['time']
                appears = now() + 3600 - late_by

            location['appears'] = appears
            location['leaves'] = appears + 900

        # Put the spawn points in order of next appearance time
        self.locations.sort(key=itemgetter('appears'))

        # Match expected structure:
        # locations = [((lat, lng, alt), ts_appears, ts_leaves),...]
        retset = []
        for step, location in enumerate(self.locations, 1):
            retset.append((step, (location['lat'], location['lng'], 40.32), location['appears'], location['leaves']))

        return retset

    # Schedule the work to be done
    def schedule(self):
        if not self.scan_location:
            log.warning('Cannot schedule work until scan location has been set')
            return

        # SpawnScan needs to calculate the list every time, since the times will change.
        self.locations = self._generate_locations()

        for location in self.locations:
            # FUTURE IMPROVEMENT - For now, queues is assumed to have a single queue.
            self.queues[0].put(location)
            log.debug("Added location {}".format(location))

        # Clear the locations list so it gets regenerated next cycle
        self.size = len(self.locations)
        self.locations = None


# This class adds speed limiting to spawnscan
class SpawnScanSpeedLimit(BaseScheduler):
    def __init__(self, queues, status, args):
        BaseScheduler.__init__(self, queues, status, args)
        # On the first scan, we want to search the last 15 minutes worth of spawns to get existing
        # pokemon onto the map.
        self.firstscan = True

        # If we are only scanning for pokestops/gyms, the scan radius can be 900m.  Otherwise 70m
        if self.args.no_pokemon:
            self.step_distance = 0.900
        else:
            self.step_distance = 0.070

        self.step_limit = args.step_limit
        self.locations = False
        self._cached_schedule = False

    def print_status(self):
        status = ''
        if self.bad:
            status += '[{} dropped points] '.format(len(self.bad))

        if self.delays:
            status += '[{} delayed points] [{:.2f} avg delay] [{:.2f} max delay]'.format(len(self.delays), (sum(self.delays) / len(self.delays)), max(self.delays))
        return status

    # Generate locations is called when the locations list is cleared - the first time it scans or after a location change.
    def _generate_locations(self):
        # Scheduling with time in hourly-second format only needs to be calculated once
        if not self._cached_schedule:
            # Attempt to load spawns from file
            if self.args.spawnpoint_scanning != 'nofile':
                log.debug('Loading spawn points from json file @ %s', self.args.spawnpoint_scanning)
                try:
                    with open(self.args.spawnpoint_scanning) as file:
                        self.locations = json.load(file)
                except ValueError as e:
                    log.exception(e)
                    log.error('JSON error: %s; will fallback to database', e)
                except IOError as e:
                    log.error('Error opening json file: %s; will fallback to database', e)

            # No locations yet? Try the database!
            if not self.locations:
                log.debug('Loading spawn points from database')
                self.locations = Pokemon.get_spawnpoints_in_hex(self.scan_location, self.args.step_limit)

            # Run the scheduling algorithm
            # This adds a "worker" field
            self.locations, self.delays, self.bad = self.assign_spawns(self.locations)

            if len(self.bad):
                log.info('Cannot schedule %d spawnpoints under max_delay, dropping.' % len(self.bad))

            log.debug('Completed job assignment.')
            if len(self.delays):
                log.info('Number of scan delays: %d.' % len(self.delays))
                log.info('Average delay: %f seconds.' % (sum(self.delays) / len(self.delays)))
                log.info('Max delay: %f seconds.' % max(self.delays))
            else:
                log.info('No additional delay is added to any spawn point.')

            # locations[]:
            # {"lat": 37.53079079414139, "lng": -122.28811690874117, "spawnpoint_id": "808f9f1601d", "time": 511, "worker": 1}

            log.info('Total of %d spawns to track', len(self.locations))

            # locations.sort(key=itemgetter('time'))

            if self.args.very_verbose:
                for i in self.locations:
                    sec = i['scan_time'] % 60
                    minute = (i['scan_time'] / 60) % 60
                    m = 'Scan [{:02}:{:02}] ({}) @ {},{}'.format(minute, sec, i['scan_time'], i['lat'], i['lng'])
                    log.debug(m)

            self._cached_schedule = self.locations
        else:
            self.locations = self._cached_schedule

        # TODO/COMMENT: sps_scan_current is in conflict with speed limiting
        # 'time' from json and db alike has been munged to appearance time as seconds after the hour
        # Here we'll convert that to a real timestamp
        for location in self.locations:
            location['scan_time'] = now() + (location['scan_time'] - cur_sec()) % 3600
            location['leaves'] = now() + (location['time'] - cur_sec()) % 3600 + 900

        # Put the spawn points in order of the scheduled scan time
        self.locations.sort(key=itemgetter('scan_time'))

        # Match expected structure:
        # locations = [((lat, lng, alt), ts_scan_time, ts_leaves),...]
        retset = [(location['worker'], step, (location['lat'], location['lng'],
                   40.32), location['scan_time'], location['leaves']) for step,
                  location in enumerate(self.locations, 1)]

        return retset

    # Schedule the work to be done
    # This is invoked if and noly if one of the queues are empty
    # Our job here is to fill those that are empty
    def schedule(self):
        if not self.scan_location:
            log.warning('Cannot schedule work until scan location has been set')
            return

        # SpawnScan needs to calculate the list every time, since the times will change.
        self.locations = self._generate_locations()

        to_fill = [i for i, q in enumerate(self.queues) if q.empty()]
        # Fill-in all the spawns of the next hour into empty queues
        for location in self.locations:
            if location[0] in to_fill:
                self.queues[location[0]].put(location[1:])
                log.debug("Added location {} to queue {}".format(location[1:], location[0]))

        # Clear the locations list so it gets regenerated next cycle
        self.size = len(self.locations)
        self.locations = None

    def assign_spawns(self, spawns):

        log.info('Attemping to assign %d spawn points to %d accounts' % (len(spawns), self.args.workers))

        def dist(sp1, sp2):
            dist = geopy.distance.distance((sp1['lat'], sp1['lng']), (sp2['lat'], sp2['lng'])).meters
            return dist

        def speed(sp1, sp2):
            time = max((sp2['scan_time'] - sp1['scan_time']) % 3600, self.args.scan_delay)
            if time == 0:
                return float('inf')
            else:
                return dist(sp1, sp2) / time

        # Insert has has two modes of operation.
        # If dry=True, it will simulate inserting sp and return the "cost" of
        # assigning sp to queue. The cost is a tuple (delay, s0, s1, s2). delay is
        # the delay incurred, s1 is the speed that the worker need to travel to
        # scan sp, s2 is the speed that the worker need to travel after scanning
        # sp, and s0 = max(s1, s2)
        # If dry=False, it will insert sp to the proper location
        def insert(queue, sp, dry):
            # make a copy so we don't change the spawnpoint passed in
            sp = dict(sp)

            if len(queue) == 0:
                if not dry:
                    queue.append(sp)
                    return 0, self.args.max_speed, self.args.max_speed, self.args.max_speed
                else:
                    # Return bogus deley so that a new worker only comes in
                    # when existing workers cannot take the point with less
                    # than a thrid of max_delay
                    return self.args.max_delay / 3, self.args.max_speed, self.args.max_speed, self.args.max_speed

            # A potential position P could be scheduled between A and B if A
            # happens before P + max_delay and B happens after P
            # We also take account of scan_delay here
            potential_position = []
            for k in range(0, len(queue)):
                if queue[k]['scan_time'] <= sp['scan_time'] + self.args.max_delay - self.args.scan_delay:
                    if k == len(queue) - 1 or sp['scan_time'] + self.args.scan_delay <= queue[k + 1]['scan_time']:
                        potential_position.append(k + 1)

            # Try all possible positions to insert sp
            scores = []
            for k in potential_position:
                # i is the previous point index
                i = (k - 1) % len(queue)
                # j is the next point index
                j = k % len(queue)

                if i != j and j != 0 and queue[j]['scan_time'] < sp['scan_time'] + self.args.scan_delay:
                    continue

                # Make scan time at least scan_delay after the previous point
                sp['scan_time'] = max(sp['scan_time'], queue[i]['scan_time'] + self.args.scan_delay)
                spp = dict(sp)

                # Calculate scanner speeds incurred by adding sp
                s1 = speed(queue[i], sp)
                s2 = speed(sp, queue[j])

                if i != j and (queue[j]['scan_time'] - queue[i]['scan_time']) % 3600 < 2 * self.args.scan_delay:
                    # No room for sp
                    score = (float('inf'), 0, 0, 0)
                elif s1 <= self.args.max_speed and s2 <= self.args.max_speed:
                    # We are all good to go
                    score = (0, max(s1, s2), s1, s2)
                elif s2 > self.args.max_speed:
                    # No room for sp
                    score = (float('inf'), 0, 0, 0)
                else:
                    # s1 > max_speed, try to wiggle the scan time for sp
                    time2wait = (dist(queue[i], sp) / self.args.max_speed) - (sp['scan_time'] - queue[i]['scan_time'])
                    if time2wait > (queue[j]['scan_time'] - sp['scan_time'] - self.args.scan_delay) % 3600:
                        # Wiggle failed
                        score = (float('inf'), 0, 0, 0)
                    else:
                        # Wiggle successful, add time2wait as delay
                        spp['scan_time'] += time2wait
                        s1 = self.args.max_speed
                        s2 = speed(spp, queue[j])
                        if s2 <= self.args.max_speed:
                            score = (time2wait, max(s1, s2), s1, s2)
                        else:
                            score = (float('inf',), 0, 0, 0)
                scores.append((score, k, spp))

            # only actually try to insert into the best spot
            score, k, sp = min(scores)

            if not dry and score[0] < float('inf'):
                queue.insert(k, sp)

            return score

        # Tries to assign spawns to n workers, returns the set of delays and the
        # set of points that cannot be covered (bad).
        def greedy_assign(spawns, n):
            for sp in spawns:
                sp['scan_time'] = (sp['time'] + 10) % 3600  # 10 seconds grace period
            spawns.sort(key=itemgetter('scan_time'))
            Q = [[] for i in range(n)]
            delays = []
            bad = []
            for sp in spawns:
                scores = [(insert(q, sp, True), i) for i, q in enumerate(Q)]
                min_score, min_index = min(scores)
                delay, s0, s1, s2 = min_score
                if delay <= self.args.max_delay:
                    insert(Q[min_index], sp, False)
                    if delay > 0:
                        delays.append(delay)
                else:
                    bad.append(sp)

            log.info("Assigned %d spawn points to %d workers, left out %d points" %
                     (len(spawns) - len(bad), n, len(bad)))
            return Q, delays, bad

        Q, delays, bad = greedy_assign(spawns, self.args.workers)

        # Assign worker id to each spown point
        for index, queue in enumerate(Q):
            for sp in queue:
                sp['worker'] = index

        # Merge individual job queues back to one queue and sort it
        spawns = sum(Q, [])
        spawns.sort(key=itemgetter('scan_time'))

        return spawns, delays, bad


# The SchedulerFactory returns an instance of the correct type of scheduler
class SchedulerFactory():
    __schedule_classes = {
        "hexsearch": HexSearch,
        "hexsearchspawnpoint": HexSearchSpawnpoint,
        "spawnscan": SpawnScan,
        "spawnscanspeedlimit": SpawnScanSpeedLimit
    }

    @staticmethod
    def get_scheduler(name, *args, **kwargs):
        scheduler_class = SchedulerFactory.__schedule_classes.get(name.lower(), None)

        if scheduler_class:
            return scheduler_class(*args, **kwargs)

        raise NotImplementedError("The requested scheduler has not been implemented")

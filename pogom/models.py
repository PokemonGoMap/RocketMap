#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import itertools
import calendar
import sys
import gc
import time
import geopy
import math
from peewee import SqliteDatabase, InsertQuery, Check, ForeignKeyField, \
    IntegerField, CharField, DoubleField, BooleanField, \
    DateTimeField, fn, DeleteQuery, CompositeKey, FloatField, SQL, TextField
from playhouse.flask_utils import FlaskDB
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import RetryOperationalError
from playhouse.migrate import migrate, MySQLMigrator, SqliteMigrator
from datetime import datetime, timedelta
from base64 import b64encode
from cachetools import TTLCache
from cachetools import cached

from . import config
from .utils import get_pokemon_name, get_pokemon_rarity, get_pokemon_types, get_args, cellid, in_radius
from .transform import transform_from_wgs_to_gcj, get_new_coords
from .customLog import printPokemon

log = logging.getLogger(__name__)

args = get_args()
flaskDb = FlaskDB()
cache = TTLCache(maxsize=100, ttl=60 * 5)

db_schema_version = 8


class MyRetryDB(RetryOperationalError, PooledMySQLDatabase):
    pass


def init_database(app):
    if args.db_type == 'mysql':
        log.info('Connecting to MySQL database on %s:%i', args.db_host, args.db_port)
        connections = args.db_max_connections
        if hasattr(args, 'accounts'):
            connections *= len(args.accounts)
        db = MyRetryDB(
            args.db_name,
            user=args.db_user,
            password=args.db_pass,
            host=args.db_host,
            port=args.db_port,
            max_connections=connections,
            stale_timeout=300)
    else:
        log.info('Connecting to local SQLite database')
        db = SqliteDatabase(args.db)

    app.config['DATABASE'] = db
    flaskDb.init_app(app)

    return db


class BaseModel(flaskDb.Model):

    @classmethod
    def get_all(cls):
        results = [m for m in cls.select().dicts()]
        if args.china:
            for result in results:
                result['latitude'], result['longitude'] = \
                    transform_from_wgs_to_gcj(
                        result['latitude'], result['longitude'])
        return results


class Pokemon(BaseModel):
    # We are base64 encoding the ids delivered by the api
    # because they are too big for sqlite to handle
    encounter_id = CharField(primary_key=True, max_length=50)
    spawnpoint_id = CharField(index=True)
    pokemon_id = IntegerField(index=True)
    latitude = DoubleField()
    longitude = DoubleField()
    disappear_time = DateTimeField(index=True)

    class Meta:
        indexes = ((('latitude', 'longitude'), False),)

    @staticmethod
    def get_active(swLat, swLng, neLat, neLng):
        if swLat is None or swLng is None or neLat is None or neLng is None:
            query = (Pokemon
                     .select()
                     .where(Pokemon.disappear_time > datetime.utcnow())
                     .dicts())
        else:
            query = (Pokemon
                     .select()
                     .where((Pokemon.disappear_time > datetime.utcnow()) &
                            (((Pokemon.latitude >= swLat) &
                              (Pokemon.longitude >= swLng) &
                              (Pokemon.latitude <= neLat) &
                              (Pokemon.longitude <= neLng))))
                     .dicts())

        # Performance: Disable the garbage collector prior to creating a (potentially) large dict with append()
        gc.disable()

        pokemons = []
        for p in query:
            p['pokemon_name'] = get_pokemon_name(p['pokemon_id'])
            p['pokemon_rarity'] = get_pokemon_rarity(p['pokemon_id'])
            p['pokemon_types'] = get_pokemon_types(p['pokemon_id'])
            if args.china:
                p['latitude'], p['longitude'] = \
                    transform_from_wgs_to_gcj(p['latitude'], p['longitude'])
            pokemons.append(p)

        # Re-enable the GC.
        gc.enable()

        return pokemons

    @staticmethod
    def get_active_by_id(ids, swLat, swLng, neLat, neLng):
        if swLat is None or swLng is None or neLat is None or neLng is None:
            query = (Pokemon
                     .select()
                     .where((Pokemon.pokemon_id << ids) &
                            (Pokemon.disappear_time > datetime.utcnow()))
                     .dicts())
        else:
            query = (Pokemon
                     .select()
                     .where((Pokemon.pokemon_id << ids) &
                            (Pokemon.disappear_time > datetime.utcnow()) &
                            (Pokemon.latitude >= swLat) &
                            (Pokemon.longitude >= swLng) &
                            (Pokemon.latitude <= neLat) &
                            (Pokemon.longitude <= neLng))
                     .dicts())

        # Performance: Disable the garbage collector prior to creating a (potentially) large dict with append()
        gc.disable()

        pokemons = []
        for p in query:
            p['pokemon_name'] = get_pokemon_name(p['pokemon_id'])
            p['pokemon_rarity'] = get_pokemon_rarity(p['pokemon_id'])
            p['pokemon_types'] = get_pokemon_types(p['pokemon_id'])
            if args.china:
                p['latitude'], p['longitude'] = \
                    transform_from_wgs_to_gcj(p['latitude'], p['longitude'])
            pokemons.append(p)

        # Re-enable the GC.
        gc.enable()

        return pokemons

    @classmethod
    @cached(cache)
    def get_seen(cls, timediff):
        if timediff:
            timediff = datetime.utcnow() - timediff
        pokemon_count_query = (Pokemon
                               .select(Pokemon.pokemon_id,
                                       fn.COUNT(Pokemon.pokemon_id).alias('count'),
                                       fn.MAX(Pokemon.disappear_time).alias('lastappeared')
                                       )
                               .where(Pokemon.disappear_time > timediff)
                               .group_by(Pokemon.pokemon_id)
                               .alias('counttable')
                               )
        query = (Pokemon
                 .select(Pokemon.pokemon_id,
                         Pokemon.disappear_time,
                         Pokemon.latitude,
                         Pokemon.longitude,
                         pokemon_count_query.c.count)
                 .join(pokemon_count_query, on=(Pokemon.pokemon_id == pokemon_count_query.c.pokemon_id))
                 .distinct()
                 .where(Pokemon.disappear_time == pokemon_count_query.c.lastappeared)
                 .dicts()
                 )

        # Performance: Disable the garbage collector prior to creating a (potentially) large dict with append()
        gc.disable()

        pokemons = []
        total = 0
        for p in query:
            p['pokemon_name'] = get_pokemon_name(p['pokemon_id'])
            pokemons.append(p)
            total += p['count']

        # Re-enable the GC.
        gc.enable()

        return {'pokemon': pokemons, 'total': total}

    @classmethod
    def get_appearances(cls, pokemon_id, timediff):
        '''
        :param pokemon_id: id of pokemon that we need appearances for
        :param timediff: limiting period of the selection
        :return: list of  pokemon  appearances over a selected period
        '''
        if timediff:
            timediff = datetime.utcnow() - timediff
        query = (Pokemon
                 .select(Pokemon.latitude, Pokemon.longitude, Pokemon.pokemon_id, fn.Count(Pokemon.spawnpoint_id).alias('count'), Pokemon.spawnpoint_id)
                 .where((Pokemon.pokemon_id == pokemon_id) &
                        (Pokemon.disappear_time > timediff)
                        )
                 .group_by(Pokemon.latitude, Pokemon.longitude, Pokemon.pokemon_id, Pokemon.spawnpoint_id)
                 .dicts()
                 )

        return list(query)

    @classmethod
    def get_appearances_times_by_spawnpoint(cls, pokemon_id, spawnpoint_id, timediff):
        '''
        :param pokemon_id: id of pokemon that we need appearances times for
        :param spawnpoint_id: spawnpoing id we need appearances times for
        :param timediff: limiting period of the selection
        :return: list of time appearances over a selected period
        '''
        if timediff:
            timediff = datetime.utcnow() - timediff
        query = (Pokemon
                 .select(Pokemon.disappear_time)
                 .where((Pokemon.pokemon_id == pokemon_id) &
                        (Pokemon.spawnpoint_id == spawnpoint_id) &
                        (Pokemon.disappear_time > timediff)
                        )
                 .order_by(Pokemon.disappear_time.asc())
                 .tuples()
                 )

        return list(itertools.chain(*query))

    @classmethod
    def get_spawn_time(cls, disappear_time):
        return (disappear_time + 2700) % 3600

    @classmethod
    def get_spawnpoints(cls, southBoundary, westBoundary, northBoundary, eastBoundary):
        query = Pokemon.select(Pokemon.latitude, Pokemon.longitude, Pokemon.spawnpoint_id, ((Pokemon.disappear_time.minute * 60) + Pokemon.disappear_time.second).alias('time'), fn.Count(Pokemon.spawnpoint_id).alias('count'))

        if None not in (northBoundary, southBoundary, westBoundary, eastBoundary):
            query = (query
                     .where((Pokemon.latitude <= northBoundary) &
                            (Pokemon.latitude >= southBoundary) &
                            (Pokemon.longitude >= westBoundary) &
                            (Pokemon.longitude <= eastBoundary)
                            ))

        query = query.group_by(Pokemon.latitude, Pokemon.longitude, Pokemon.spawnpoint_id, SQL('time'))

        queryDict = query.dicts()
        spawnpoints = {}

        for sp in queryDict:
            key = sp['spawnpoint_id']
            disappear_time = cls.get_spawn_time(sp.pop('time'))
            count = int(sp['count'])

            if key not in spawnpoints:
                spawnpoints[key] = sp
            else:
                spawnpoints[key]['special'] = True

            if 'time' not in spawnpoints[key] or count >= spawnpoints[key]['count']:
                spawnpoints[key]['time'] = disappear_time
                spawnpoints[key]['count'] = count

        for sp in spawnpoints.values():
            del sp['count']

        return list(spawnpoints.values())

    @classmethod
    def get_spawnpoints_in_hex(cls, center, steps):
        log.info('Finding spawn points {} steps away'.format(steps))

        n, e, s, w = hex_bounds(center, steps)

        query = (Pokemon
                 .select(Pokemon.latitude.alias('lat'),
                         Pokemon.longitude.alias('lng'),
                         ((Pokemon.disappear_time.minute * 60) + Pokemon.disappear_time.second).alias('time'),
                         Pokemon.spawnpoint_id
                         ))
        query = (query.where((Pokemon.latitude <= n) &
                             (Pokemon.latitude >= s) &
                             (Pokemon.longitude >= w) &
                             (Pokemon.longitude <= e)
                             ))
        # Sqlite doesn't support distinct on columns
        if args.db_type == 'mysql':
            query = query.distinct(Pokemon.spawnpoint_id)
        else:
            query = query.group_by(Pokemon.spawnpoint_id)

        s = list(query.dicts())

        # The distance between scan circles of radius 70 in a hex is 121.2436
        # steps - 1 to account for the center circle then add 70 for the edge
        step_distance = ((steps - 1) * 121.2436) + 70
        # Compare spawnpoint list to a circle with radius steps * 120
        # Uses the direct geopy distance between the center and the spawnpoint.
        filtered = []

        for idx, sp in enumerate(s):
            if geopy.distance.distance(center, (sp['lat'], sp['lng'])).meters <= step_distance:
                filtered.append(s[idx])

        # at this point, 'time' is DISAPPEARANCE time, we're going to morph it to APPEARANCE time
        for location in filtered:
            # examples: time    shifted
            #           0       (   0 + 2700) = 2700 % 3600 = 2700 (0th minute to 45th minute, 15 minutes prior to appearance as time wraps around the hour)
            #           1800    (1800 + 2700) = 4500 % 3600 =  900 (30th minute, moved to arrive at 15th minute)
            # todo: this DOES NOT ACCOUNT for pokemons that appear sooner and live longer, but you'll _always_ have at least 15 minutes, so it works well enough
            location['time'] = cls.get_spawn_time(location['time'])

        return filtered


class Pokestop(BaseModel):
    pokestop_id = CharField(primary_key=True, max_length=50)
    enabled = BooleanField()
    latitude = DoubleField()
    longitude = DoubleField()
    last_modified = DateTimeField(index=True)
    lure_expiration = DateTimeField(null=True, index=True)
    active_fort_modifier = CharField(max_length=50, null=True)

    class Meta:
        indexes = ((('latitude', 'longitude'), False),)

    @staticmethod
    def get_stops(swLat, swLng, neLat, neLng):
        if swLat is None or swLng is None or neLat is None or neLng is None:
            query = (Pokestop
                     .select()
                     .dicts())
        else:
            query = (Pokestop
                     .select()
                     .where((Pokestop.latitude >= swLat) &
                            (Pokestop.longitude >= swLng) &
                            (Pokestop.latitude <= neLat) &
                            (Pokestop.longitude <= neLng))
                     .dicts())

        # Performance: Disable the garbage collector prior to creating a (potentially) large dict with append()
        gc.disable()

        pokestops = []
        for p in query:
            if args.china:
                p['latitude'], p['longitude'] = \
                    transform_from_wgs_to_gcj(p['latitude'], p['longitude'])
            pokestops.append(p)

        # Re-enable the GC.
        gc.enable()

        return pokestops


class Gym(BaseModel):
    UNCONTESTED = 0
    TEAM_MYSTIC = 1
    TEAM_VALOR = 2
    TEAM_INSTINCT = 3

    gym_id = CharField(primary_key=True, max_length=50)
    team_id = IntegerField()
    guard_pokemon_id = IntegerField()
    gym_points = IntegerField()
    enabled = BooleanField()
    latitude = DoubleField()
    longitude = DoubleField()
    last_modified = DateTimeField(index=True)
    last_scanned = DateTimeField(default=datetime.utcnow)

    class Meta:
        indexes = ((('latitude', 'longitude'), False),)

    @staticmethod
    def get_gyms(swLat, swLng, neLat, neLng):
        if swLat is None or swLng is None or neLat is None or neLng is None:
            results = (Gym
                       .select()
                       .dicts())
        else:
            results = (Gym
                       .select()
                       .where((Gym.latitude >= swLat) &
                              (Gym.longitude >= swLng) &
                              (Gym.latitude <= neLat) &
                              (Gym.longitude <= neLng))
                       .dicts())

        # Performance: Disable the garbage collector prior to creating a (potentially) large dict with append()
        gc.disable()

        gyms = {}
        gym_ids = []
        for g in results:
            g['name'] = None
            g['pokemon'] = []
            gyms[g['gym_id']] = g
            gym_ids.append(g['gym_id'])

        if len(gym_ids) > 0:
            pokemon = (GymMember
                       .select(
                           GymMember.gym_id,
                           GymPokemon.cp.alias('pokemon_cp'),
                           GymPokemon.pokemon_id,
                           Trainer.name.alias('trainer_name'),
                           Trainer.level.alias('trainer_level'))
                       .join(Gym, on=(GymMember.gym_id == Gym.gym_id))
                       .join(GymPokemon, on=(GymMember.pokemon_uid == GymPokemon.pokemon_uid))
                       .join(Trainer, on=(GymPokemon.trainer_name == Trainer.name))
                       .where(GymMember.gym_id << gym_ids)
                       .where(GymMember.last_scanned > Gym.last_modified)
                       .order_by(GymMember.gym_id, GymPokemon.cp)
                       .dicts())

            for p in pokemon:
                p['pokemon_name'] = get_pokemon_name(p['pokemon_id'])
                gyms[p['gym_id']]['pokemon'].append(p)

            details = (GymDetails
                       .select(
                           GymDetails.gym_id,
                           GymDetails.name)
                       .where(GymDetails.gym_id << gym_ids)
                       .dicts())

            for d in details:
                gyms[d['gym_id']]['name'] = d['name']

        # Re-enable the GC.
        gc.enable()

        return gyms


class ScannedLocation(BaseModel):
    cellid = CharField(primary_key=True, max_length=50)
    latitude = DoubleField()
    longitude = DoubleField()
    last_modified = DateTimeField(index=True, null=True)

    # marked true when all five bands have been completed
    done = BooleanField(default=False)

    # Five scans/hour is required to catch all spawns
    # Each scan must be at least 12 minutes from the previous check,
    # with a 2 minute window during which the scan can be done

    # default of -1 is for bands not yet scanned
    band1 = IntegerField(default=-1, constraints=[Check('band1 >= -1'), Check('band1 < 3600')])
    band2 = IntegerField(default=-1, constraints=[Check('band2 >= -1'), Check('band2 < 3600')])
    band3 = IntegerField(default=-1, constraints=[Check('band3 >= -1'), Check('band3 < 3600')])
    band4 = IntegerField(default=-1, constraints=[Check('band4 >= -1'), Check('band4 < 3600')])
    band5 = IntegerField(default=-1, constraints=[Check('band5 >= -1'), Check('band5 < 3600')])

    # midpoint is the center of the bands relative to band 1
    # e.g., if band 1 is 10.4 min, and band 4 is 34.0 min, midpoint is -0.2 min in minsec
    # extra 10 seconds in case of delay in recording now time
    midpoint = IntegerField(default=0, constraints=[Check('midpoint >= -130'), Check('midpoint <= 130')])

    # width is how wide the valid window is. Default is 0, max is 2 min
    # e.g., if band 1 is 10.4 min, and band 4 is 34.0 min, midpoint is 0.4 min in minsec
    width = IntegerField(default=0, constraints=[Check('width >= 0'), Check('width <= 120')])

    class Meta:
        indexes = ((('latitude', 'longitude'), False),)

    @staticmethod
    def get_recent(swLat, swLng, neLat, neLng):
        query = (ScannedLocation
                 .select()
                 .where((ScannedLocation.last_modified >=
                        (datetime.utcnow() - timedelta(minutes=15))) &
                        (ScannedLocation.latitude >= swLat) &
                        (ScannedLocation.longitude >= swLng) &
                        (ScannedLocation.latitude <= neLat) &
                        (ScannedLocation.longitude <= neLng))
                 .order_by(ScannedLocation.last_modified.asc())
                 .dicts())

        return list(query)

    # Used to update bands
    @staticmethod
    def db_format(scan, band, nowms):
        scan.update({'band' + str(band): nowms})
        scan['done'] = reduce(lambda x, y: x and (scan['band' + str(y)] > -1), range(1, 6), True)
        return scan

    # Shorthand helper for DB dict
    @staticmethod
    def _q_init(scan, start, end, kind, sp_id=None):
        return {'loc': scan['loc'], 'kind': kind, 'start': start, 'end': end, 'step': scan['step'], 'sp': sp_id}

    # return value of a particular scan from loc, or default dict if not found
    @classmethod
    def get_by_loc(cls, loc):
        query = (cls
                 .select()
                 .where((ScannedLocation.latitude == loc[0]) &
                        (ScannedLocation.longitude == loc[1]))
                 .dicts())

        return query[0] if len(list(query)) else {'cellid': cellid(loc),
                                                  'latitude': loc[0],
                                                  'longitude': loc[1],
                                                  'done': False,
                                                  'band1': -1,
                                                  'band2': -1,
                                                  'band3': -1,
                                                  'band4': -1,
                                                  'band5': -1,
                                                  'width': 0,
                                                  'midpoint': 0,
                                                  'last_modified': None}

    # Check if spawn points in a list are in any of the existing spannedlocation records
    # Otherwise, search through the spawn point list, and update scan_spawn_point dict for DB bulk upserting
    @classmethod
    def get_spawn_points(cls, scans, spawn_points, distance, scan_spawn_point):
        for cell, scan in scans.iteritems():
            # Pass on cells that have been scanned at least once before
            if cls.get_by_loc(scan['loc'])['band1'] > -1:
                continue

            # Otherwise, do a search of spawn points from the list to see if in range
            for sp in spawn_points:
                if in_radius((sp['latitude'], sp['longitude']), scan['loc'], distance):
                    scan_spawn_point[cell + sp['id']] = {'spawnpoint': sp['id'],
                                                         'scannedlocation': cell}

    # return list of dicts for upcoming valid band times
    @classmethod
    def linked_spawn_points(cls, cell):
        query = (SpawnPoint
                 .select()
                 .join(ScanSpawnPoint)
                 .join(cls)
                 .where(cls.cellid == cell).dicts())

        return list(query)

    # return list of dicts for upcoming valid band times
    @staticmethod
    def visible_forts(step_location):
        distance = 0.9
        n, e, s, w = hex_bounds(step_location, radius=distance * 1000)
        for g in Gym.get_gyms(s, w, n, e).values():
            if in_radius((g['latitude'], g['longitude']), step_location, distance):
                return True

        for g in Pokestop.get_stops(s, w, n, e):
            if in_radius((g['latitude'], g['longitude']), step_location, distance):
                return True

        return False

    # return list of dicts for upcoming valid band times
    @classmethod
    def get_times(cls, scan, now_date):
        s = cls.get_by_loc(scan['loc'])
        if s['done']:
            return []

        max = 3600 * 2 + 250  # greater than maximum possible value
        min = {'end': max}

        nowms = now_date.minute * 60 + now_date.second
        if s['band1'] == -1:
            return [cls._q_init(scan, nowms, nowms + 3600, 'band')]

        # Find next window
        basems = s['band1']
        for i in range(2, 6):
            ms = s['band' + str(i)]

            # skip bands already done
            if ms > -1:
                continue

            radius = 120 - s['width'] / 2
            end = (basems + s['midpoint'] + radius + (i - 1) * 720 - 5) % 3600
            end = end if end >= nowms else end + 3600

            if end < min['end']:
                min = cls._q_init(scan, end - radius * 2, end, 'band')

        return [min] if min['end'] < max else []

    # Checks if now falls within an unfilled band for a scanned location
    # Returns the updated scan location dict
    @classmethod
    def update_band(cls, loc):
        scan = cls.get_by_loc(loc)
        now_date = datetime.utcnow()
        scan['last_modified'] = now_date

        if scan['done']:
            return scan

        now_ms = now_date.minute * 60 + now_date.second
        if scan['band1'] == -1:
            return cls.db_format(scan, 1, now_ms)

        # calc if number falls in band with remaining points
        basems = scan['band1']
        delta = (now_ms - basems - scan['midpoint'] + 3600) % 3600
        band = int(round(delta / 12 / 60.0) % 5) + 1

        # Check if that band already filled
        if scan['band' + str(band)] > -1:
            return scan

        # Check if this result falls within the band 2 min window
        offset = (delta + 1080) % 720 - 360
        if abs(offset) > 120 - scan['width'] / 2:
            return scan

        # find band midpoint/width
        scan = cls.db_format(scan, band, now_ms)
        bts = [scan['band' + str(i)] for i in range(1, 6)]
        bts = filter(lambda ms: ms > -1, bts)
        bts_delta = map(lambda ms: (ms - basems + 3600) % 3600, bts)
        bts_offsets = map(lambda ms: (ms + 1080) % 720 - 360, bts_delta)
        min_scan = min(bts_offsets)
        max_scan = max(bts_offsets)
        scan['width'] = max_scan - min_scan
        scan['midpoint'] = (max_scan + min_scan) / 2

        return scan

    @classmethod
    def bands_filled(cls, locations):
        filled = 0
        for e in locations:
            sl = cls.get_by_loc(e[1])
            bands = [sl['band' + str(i)] for i in range(1, 6)]
            filled += reduce(lambda x, y: x + (y > -1), bands, 0)

        return filled


class MainWorker(BaseModel):
    worker_name = CharField(primary_key=True, max_length=50)
    message = CharField()
    method = CharField(max_length=50)
    last_modified = DateTimeField(index=True)


class WorkerStatus(BaseModel):
    username = CharField(primary_key=True, max_length=50)
    worker_name = CharField()
    success = IntegerField()
    fail = IntegerField()
    no_items = IntegerField()
    skip = IntegerField()
    last_modified = DateTimeField(index=True)
    message = CharField(max_length=255)
    last_scan_date = DateTimeField(index=True)
    latitude = DoubleField(default=0)
    longitude = DoubleField(default=0)

    @staticmethod
    def db_format(status):
        return {'username': status['user'],
                'worker_name': 'status_worker_db',
                'success': status['success'],
                'fail': status['fail'],
                'no_items': status['noitems'],
                'skip': status['skip'],
                'last_modified': datetime.utcnow(),
                'message': status['message'],
                'last_scan_date': status['last_scan_date'],
                'latitude': status['location'][0],
                'longitude': status['location'][1]}

    @staticmethod
    def get_recent():
        query = (WorkerStatus
                 .select()
                 .where((WorkerStatus.last_modified >=
                        (datetime.utcnow() - timedelta(minutes=5))))
                 .order_by(WorkerStatus.username)
                 .dicts())

        status = []
        for s in query:
            status.append(s)

        return status

    @staticmethod
    def get_worker(username):
        query = (WorkerStatus
                 .select()
                 .where((WorkerStatus.username == username))
                 .dicts())

        return query[0] if query else None


class SpawnPoint(BaseModel):
    id = CharField(primary_key=True, max_length=50)
    latitude = DoubleField()
    longitude = DoubleField()
    despawn_time = IntegerField(constraints=[Check('despawn_time >= 0'), Check('despawn_time < 3600')], null=True)
    last_modified = DateTimeField(index=True)

    class Meta:
        indexes = ((('latitude', 'longitude'), False),)

    # Returns the spawn point dict from ID
    @classmethod
    def get_by_id(cls, id):
        query = (cls
                 .select()
                 .where(cls.id == id)
                 .dicts())

        return query[0] if query else []

    # Check if spawn points are in any of the existing spannedlocation records
    # Update scan_spawn_points for DB bulk upserting
    @staticmethod
    def add_to_scans(sp, scan_spawn_points):
        for sl in ScannedLocation.select():
            if in_radius((sp['latitude'], sp['longitude']), (sl.latitude, sl.longitude), 0.07):
                scan_spawn_points[sl.cellid + sp['id']] = {'spawnpoint': sp['id'],
                                                           'scannedlocation': sl.cellid}

    # Return a list of dicts with the next spawn times
    @classmethod
    def get_times(cls, cell, scan, now_date, scan_delay):
        l = []
        now_ms = now_date.minute * 60 + now_date.second
        for sp in ScannedLocation.linked_spawn_points(cell):
            end = sp['despawn_time']
            if end < now_ms:
                end += 3600

            start = end - 15 * 60 + scan_delay  # one minute buffer to ensure spawned

            if (now_date - cls.get_by_id(sp['id'])['last_modified']).total_seconds() <= now_ms - start:
                continue

            l.append(ScannedLocation._q_init(scan, start, end, 'spawn', sp['id']))

        return l

    @classmethod
    def select_in_hex(cls, center, steps):
        R = 6378.1  # km radius of the earth
        hdist = ((steps * 120.0) - 50.0) / 1000.0
        n, e, s, w = hex_bounds(center, steps)

        # get all spawns in that box
        sp = list(cls
                  .select()
                  .where((cls.latitude <= n) &
                         (cls.latitude >= s) &
                         (cls.longitude >= w) &
                         (cls.longitude <= e))
                  .dicts())

        # for each spawn work out if it is in the hex (clipping the diagonals)
        trueSpawns = []
        for spawn in sp:
            # get the offset from the center of each spawn in km
            offset = [math.radians(spawn['latitude'] - center[0]) * R,
                      math.radians(spawn['longitude'] - center[1]) * (R * math.cos(math.radians(center[0])))]
            # check agains the 4 lines that make up the diagonals
            if (offset[1] + (offset[0] * 0.5)) > hdist:  # too far ne
                continue
            if (offset[1] - (offset[0] * 0.5)) > hdist:  # too far se
                continue
            if ((offset[0] * 0.5) - offset[1]) > hdist:  # too far nw
                continue
            if ((0 - offset[1]) - (offset[0] * 0.5)) > hdist:  # too far sw
                continue
            # if it gets to here its  a good spawn
            trueSpawns.append(spawn)
        return trueSpawns


class ScanSpawnPoint(BaseModel):
    scannedlocation = ForeignKeyField(ScannedLocation)
    spawnpoint = ForeignKeyField(SpawnPoint)

    class Meta:
        primary_key = CompositeKey('scannedlocation', 'spawnpoint')


class SpawnSighting(BaseModel):
    id = CharField(primary_key=True, max_length=54)
    encounter_id = CharField(max_length=50)
    spawnpoint = ForeignKeyField(SpawnPoint)
    scan_time = DateTimeField()
    tth_ms = IntegerField(null=True)


class Versions(flaskDb.Model):
    key = CharField()
    val = IntegerField()

    class Meta:
        primary_key = False


class GymMember(BaseModel):
    gym_id = CharField(index=True)
    pokemon_uid = CharField()
    last_scanned = DateTimeField(default=datetime.utcnow)

    class Meta:
        primary_key = False


class GymPokemon(BaseModel):
    pokemon_uid = CharField(primary_key=True, max_length=50)
    pokemon_id = IntegerField()
    cp = IntegerField()
    trainer_name = CharField()
    num_upgrades = IntegerField(null=True)
    move_1 = IntegerField(null=True)
    move_2 = IntegerField(null=True)
    height = FloatField(null=True)
    weight = FloatField(null=True)
    stamina = IntegerField(null=True)
    stamina_max = IntegerField(null=True)
    cp_multiplier = FloatField(null=True)
    additional_cp_multiplier = FloatField(null=True)
    iv_defense = IntegerField(null=True)
    iv_stamina = IntegerField(null=True)
    iv_attack = IntegerField(null=True)
    last_seen = DateTimeField(default=datetime.utcnow)


class Trainer(BaseModel):
    name = CharField(primary_key=True, max_length=50)
    team = IntegerField()
    level = IntegerField()
    last_seen = DateTimeField(default=datetime.utcnow)


class GymDetails(BaseModel):
    gym_id = CharField(primary_key=True, max_length=50)
    name = CharField()
    description = TextField(null=True, default="")
    url = CharField()
    last_scanned = DateTimeField(default=datetime.utcnow)


def hex_bounds(center, steps=None, radius=None):
    # Make a box that is (70m * step_limit * 2) + 70m away from the center point
    # Rationale is that you need to travel
    sp_dist = 0.07 * (2 * steps + 1) if steps else radius
    n = get_new_coords(center, sp_dist, 0)[0]
    e = get_new_coords(center, sp_dist, 90)[1]
    s = get_new_coords(center, sp_dist, 180)[0]
    w = get_new_coords(center, sp_dist, 270)[1]
    return (n, e, s, w)


# todo: this probably shouldn't _really_ be in "models" anymore, but w/e
def parse_map(args, map_dict, step_location, db_update_queue, wh_update_queue):
    pokemons = {}
    pokestops = {}
    gyms = {}
    spawn_points = {}
    scan_spawn_points = {}
    sightings = {}
    d_t_stamp = False
    new_spawn_points = []
    bad_scan = True  # Guilty until proven innocent

    cells = map_dict['responses']['GET_MAP_OBJECTS']['map_cells']
    for cell in cells:
        if config['parse_pokemon']:
            for p in cell.get('wild_pokemons', []):
                # time_till_hidden_ms was overflowing causing a negative integer. It was also returning a value above 3.6M ms.
                if (0 < p['time_till_hidden_ms'] < 3600000):
                    d_t_stamp = (p['last_modified_timestamp_ms'] + p['time_till_hidden_ms'])
                    d_t = datetime.utcfromtimestamp(d_t_stamp / 1000.0)
                else:
                    # Set a value of 15 minutes because currently its unknown but larger than 15.
                    d_t = datetime.utcfromtimestamp((p['last_modified_timestamp_ms'] + 900000) / 1000.0)
                    d_t_stamp = False

                printPokemon(p['pokemon_data']['pokemon_id'], p['latitude'],
                             p['longitude'], d_t)
                pokemons[p['encounter_id']] = {
                    'encounter_id': b64encode(str(p['encounter_id'])),
                    'spawnpoint_id': p['spawn_point_id'],
                    'pokemon_id': p['pokemon_data']['pokemon_id'],
                    'latitude': p['latitude'],
                    'longitude': p['longitude'],
                    'disappear_time': d_t
                }

                now_stamp = datetime.utcfromtimestamp(p['last_modified_timestamp_ms'] / 1000.0)
                now_ms = now_stamp.minute * 60 + now_stamp.second
                tth_ms = d_t.minute * 60 + d_t.second if d_t_stamp else None

                sightings[p['encounter_id']] = {
                    'id': b64encode(str(p['encounter_id'])) + '_' + str(now_ms),
                    'encounter_id': b64encode(str(p['encounter_id'])),
                    'spawnpoint': p['spawn_point_id'],
                    'scan_time': now_stamp,
                    'tth_ms': tth_ms
                }

                if args.webhooks:
                    wh_update_queue.put(('pokemon', {
                        'encounter_id': b64encode(str(p['encounter_id'])),
                        'spawnpoint_id': p['spawn_point_id'],
                        'pokemon_id': p['pokemon_data']['pokemon_id'],
                        'latitude': p['latitude'],
                        'longitude': p['longitude'],
                        'disappear_time': calendar.timegm(d_t.timetuple()),
                        'last_modified_time': p['last_modified_timestamp_ms'],
                        'time_until_hidden_ms': p['time_till_hidden_ms']
                    }))

                # using existance of d_t_stamp to confirm we have a spawn time
                if d_t_stamp:
                    spawn_points[p['encounter_id']] = {
                        'id': p['spawn_point_id'],
                        'latitude': p['latitude'],
                        'longitude': p['longitude'],
                        'last_modified': now_stamp,
                        'despawn_time': tth_ms
                    }

                    if not SpawnPoint.get_by_id(p['spawn_point_id']):
                        log.info('New Spawn Point found!')
                        new_spawn_points.append(spawn_points[p['encounter_id']])
                        SpawnPoint.add_to_scans(spawn_points[p['encounter_id']], scan_spawn_points)

        for f in cell.get('forts', []):
            if config['parse_pokestops'] and f.get('type') == 1:  # Pokestops
                if 'active_fort_modifier' in f:
                    lure_expiration = datetime.utcfromtimestamp(
                        f['last_modified_timestamp_ms'] / 1000.0) + timedelta(minutes=30)
                    active_fort_modifier = f['active_fort_modifier']
                    if args.webhooks and args.webhook_updates_only:
                        wh_update_queue.put(('pokestop', {
                            'pokestop_id': b64encode(str(f['id'])),
                            'enabled': f['enabled'],
                            'latitude': f['latitude'],
                            'longitude': f['longitude'],
                            'last_modified_time': f['last_modified_timestamp_ms'],
                            'lure_expiration': calendar.timegm(lure_expiration.timetuple()),
                            'active_fort_modifier': active_fort_modifier
                        }))
                else:
                    lure_expiration, active_fort_modifier = None, None

                pokestops[f['id']] = {
                    'pokestop_id': f['id'],
                    'enabled': f['enabled'],
                    'latitude': f['latitude'],
                    'longitude': f['longitude'],
                    'last_modified': datetime.utcfromtimestamp(
                        f['last_modified_timestamp_ms'] / 1000.0),
                    'lure_expiration': lure_expiration,
                    'active_fort_modifier': active_fort_modifier
                }

                # Send all pokéstops to webhooks
                if args.webhooks and not args.webhook_updates_only:
                    # Explicitly set 'webhook_data', in case we want to change the information pushed to webhooks,
                    # similar to above and previous commits.
                    l_e = None

                    if lure_expiration is not None:
                        l_e = calendar.timegm(lure_expiration.timetuple())

                    wh_update_queue.put(('pokestop', {
                        'pokestop_id': b64encode(str(f['id'])),
                        'enabled': f['enabled'],
                        'latitude': f['latitude'],
                        'longitude': f['longitude'],
                        'last_modified': calendar.timegm(pokestops[f['id']]['last_modified'].timetuple()),
                        'lure_expiration': l_e,
                        'active_fort_modifier': active_fort_modifier
                    }))

            elif config['parse_gyms'] and f.get('type') is None:  # Currently, there are only stops and gyms
                gyms[f['id']] = {
                    'gym_id': f['id'],
                    'team_id': f.get('owned_by_team', 0),
                    'guard_pokemon_id': f.get('guard_pokemon_id', 0),
                    'gym_points': f.get('gym_points', 0),
                    'enabled': f['enabled'],
                    'latitude': f['latitude'],
                    'longitude': f['longitude'],
                    'last_modified': datetime.utcfromtimestamp(
                        f['last_modified_timestamp_ms'] / 1000.0),
                }

                # Send gyms to webhooks
                if args.webhooks and not args.webhook_updates_only:
                    # Explicitly set 'webhook_data', in case we want to change the information pushed to webhooks,
                    # similar to above and previous commits.
                    wh_update_queue.put(('gym', {
                        'gym_id': b64encode(str(f['id'])),
                        'team_id': f.get('owned_by_team', 0),
                        'guard_pokemon_id': f.get('guard_pokemon_id', 0),
                        'gym_points': f.get('gym_points', 0),
                        'enabled': f['enabled'],
                        'latitude': f['latitude'],
                        'longitude': f['longitude'],
                        'last_modified': calendar.timegm(gyms[f['id']]['last_modified'].timetuple())
                    }))

    if len(pokemons):
        db_update_queue.put((Pokemon, pokemons))
    if len(pokestops):
        db_update_queue.put((Pokestop, pokestops))
    if len(gyms):
        db_update_queue.put((Gym, gyms))
    if len(spawn_points):
        db_update_queue.put((SpawnPoint, spawn_points))
        db_update_queue.put((ScanSpawnPoint, scan_spawn_points))
        db_update_queue.put((SpawnSighting, sightings))

    log.info('Parsing found %d pokemons, %d pokestops, and %d gyms',
             len(pokemons),
             len(pokestops),
             len(gyms))

    # Check the time band of the scan location to see if all bands scanned
    count = len(pokemons) + len(pokestops) + len(gyms)

    # Check for a 0/0/0 bad scan
    # If we saw nothing and there should be visible forts, it's bad
    bad_scan = not count and ScannedLocation.visible_forts(step_location)

    if not bad_scan:
        db_update_queue.put((ScannedLocation, {0: ScannedLocation.update_band(step_location)}))

    return {
        'count': count,
        'gyms': gyms,
        'spawn_points': spawn_points,
        'scan_spawn_points': scan_spawn_points,
        'bad_scan': bad_scan
    }


def parse_gyms(args, gym_responses, wh_update_queue):
    gym_details = {}
    gym_members = {}
    gym_pokemon = {}
    trainers = {}

    i = 0
    for g in gym_responses.values():
        gym_state = g['gym_state']
        gym_id = gym_state['fort_data']['id']

        gym_details[gym_id] = {
            'gym_id': gym_id,
            'name': g['name'],
            'description': g.get('description'),
            'url': g['urls'][0],
        }

        if args.webhooks:
            webhook_data = {
                'id': gym_id,
                'latitude': gym_state['fort_data']['latitude'],
                'longitude': gym_state['fort_data']['longitude'],
                'team': gym_state['fort_data'].get('owned_by_team', 0),
                'name': g['name'],
                'description': g.get('description'),
                'url': g['urls'][0],
                'pokemon': [],
            }

        for member in gym_state.get('memberships', []):
            gym_members[i] = {
                'gym_id': gym_id,
                'pokemon_uid': member['pokemon_data']['id'],
            }

            gym_pokemon[i] = {
                'pokemon_uid': member['pokemon_data']['id'],
                'pokemon_id': member['pokemon_data']['pokemon_id'],
                'cp': member['pokemon_data']['cp'],
                'trainer_name': member['trainer_public_profile']['name'],
                'num_upgrades': member['pokemon_data'].get('num_upgrades', 0),
                'move_1': member['pokemon_data'].get('move_1'),
                'move_2': member['pokemon_data'].get('move_2'),
                'height': member['pokemon_data'].get('height_m'),
                'weight': member['pokemon_data'].get('weight_kg'),
                'stamina': member['pokemon_data'].get('stamina'),
                'stamina_max': member['pokemon_data'].get('stamina_max'),
                'cp_multiplier': member['pokemon_data'].get('cp_multiplier'),
                'additional_cp_multiplier': member['pokemon_data'].get('additional_cp_multiplier', 0),
                'iv_defense': member['pokemon_data'].get('individual_defense', 0),
                'iv_stamina': member['pokemon_data'].get('individual_stamina', 0),
                'iv_attack': member['pokemon_data'].get('individual_attack', 0),
                'last_seen': datetime.utcnow(),
            }

            trainers[i] = {
                'name': member['trainer_public_profile']['name'],
                'team': gym_state['fort_data']['owned_by_team'],
                'level': member['trainer_public_profile']['level'],
                'last_seen': datetime.utcnow(),
            }

            if args.webhooks:
                webhook_data['pokemon'].append({
                    'pokemon_uid': member['pokemon_data']['id'],
                    'pokemon_id': member['pokemon_data']['pokemon_id'],
                    'cp': member['pokemon_data']['cp'],
                    'num_upgrades': member['pokemon_data'].get('num_upgrades', 0),
                    'move_1': member['pokemon_data'].get('move_1'),
                    'move_2': member['pokemon_data'].get('move_2'),
                    'height': member['pokemon_data'].get('height_m'),
                    'weight': member['pokemon_data'].get('weight_kg'),
                    'stamina': member['pokemon_data'].get('stamina'),
                    'stamina_max': member['pokemon_data'].get('stamina_max'),
                    'cp_multiplier': member['pokemon_data'].get('cp_multiplier'),
                    'additional_cp_multiplier': member['pokemon_data'].get('additional_cp_multiplier', 0),
                    'iv_defense': member['pokemon_data'].get('individual_defense', 0),
                    'iv_stamina': member['pokemon_data'].get('individual_stamina', 0),
                    'iv_attack': member['pokemon_data'].get('individual_attack', 0),
                    'trainer_name': member['trainer_public_profile']['name'],
                    'trainer_level': member['trainer_public_profile']['level'],
                })

            i += 1
        if args.webhooks:
            wh_update_queue.put(('gym_details', webhook_data))

    # All this database stuff is synchronous (not using the upsert queue) on purpose.
    # Since the search workers load the GymDetails model from the database to determine if a gym
    # needs rescanned, we need to be sure the GymDetails get fully committed to the database before moving on.
    #
    # We _could_ synchronously upsert GymDetails, then queue the other tables for
    # upsert, but that would put that Gym's overall information in a weird non-atomic state.

    # upsert all the models
    if len(gym_details):
        bulk_upsert(GymDetails, gym_details)
    if len(gym_pokemon):
        bulk_upsert(GymPokemon, gym_pokemon)
    if len(trainers):
        bulk_upsert(Trainer, trainers)

    # This needs to be completed in a transaction, because we don't wany any other thread or process
    # to mess with the GymMembers for the gyms we're updating while we're updating the bridge table.
    with flaskDb.database.transaction():
        # get rid of all the gym members, we're going to insert new records
        if len(gym_details):
            DeleteQuery(GymMember).where(GymMember.gym_id << gym_details.keys()).execute()

        # insert new gym members
        if len(gym_members):
            bulk_upsert(GymMember, gym_members)

    log.info('Upserted %d gyms and %d gym members',
             len(gym_details),
             len(gym_members))


def db_updater(args, q):
    # The forever loop
    while True:
        try:

            while True:
                try:
                    flaskDb.connect_db()
                    break
                except Exception as e:
                    log.warning('%s... Retrying', e)

            # Loop the queue
            while True:
                model, data = q.get()
                bulk_upsert(model, data)
                q.task_done()
                log.debug('Upserted to %s, %d records (upsert queue remaining: %d)',
                          model.__name__,
                          len(data),
                          q.qsize())
                if q.qsize() > 50:
                    log.warning("DB queue is > 50 (@%d); try increasing --db-threads", q.qsize())

        except Exception as e:
            log.exception('Exception in db_updater: %s', e)


def clean_db_loop(args):
    while True:
        try:
            query = (MainWorker
                     .delete()
                     .where((ScannedLocation.last_modified <
                             (datetime.utcnow() - timedelta(minutes=30)))))
            query.execute()

            query = (WorkerStatus
                     .delete()
                     .where((ScannedLocation.last_modified <
                             (datetime.utcnow() - timedelta(minutes=30)))))
            query.execute()

            # Remove active modifier from expired lured pokestops
            query = (Pokestop
                     .update(lure_expiration=None)
                     .where(Pokestop.lure_expiration < datetime.utcnow()))
            query.execute()

            # If desired, clear old pokemon spawns
            if args.purge_data > 0:
                query = (Pokemon
                         .delete()
                         .where((Pokemon.disappear_time <
                                (datetime.utcnow() - timedelta(hours=args.purge_data)))))
                query.execute()

            log.info('Regular database cleaning complete')
            time.sleep(60)
        except Exception as e:
            log.exception('Exception in clean_db_loop: %s', e)


def bulk_upsert(cls, data):
    num_rows = len(data.values())
    i = 0

    if args.db_type == 'mysql':
        step = 120
    else:
        # SQLite has a default max number of parameters of 999,
        # so we need to limit how many rows we insert for it.
        step = 50

    while i < num_rows:
        log.debug('Inserting items %d to %d', i, min(i + step, num_rows))
        try:
            InsertQuery(cls, rows=data.values()[i:min(i + step, num_rows)]).upsert().execute()
        except Exception as e:
            # if there is a DB table constraint error, dump the data and don't retry
            if 'constraint' in str(e) or 'has no attribute' in str(e):
                log.warning('%s. Data is:', e)
                log.warning(data.items())
            else:
                log.warning('%s... Retrying', e)
                continue

        i += step


def create_tables(db):
    db.connect()
    verify_database_schema(db)
    db.create_tables([Pokemon, Pokestop, Gym, ScannedLocation, GymDetails, GymMember, GymPokemon,
                      Trainer, MainWorker, WorkerStatus, SpawnPoint, ScanSpawnPoint, SpawnSighting], safe=True)
    db.close()


def drop_tables(db):
    db.connect()
    db.drop_tables([Pokemon, Pokestop, Gym, ScannedLocation, Versions, GymDetails, GymMember, GymPokemon,
                    Trainer, MainWorker, WorkerStatus, SpawnPoint, ScanSpawnPoint, SpawnSighting, Versions], safe=True)
    db.close()


def verify_database_schema(db):
    if not Versions.table_exists():
        db.create_tables([Versions])

        if ScannedLocation.table_exists():
            # Versions table didn't exist, but there were tables. This must mean the user
            # is coming from a database that existed before we started tracking the schema
            # version. Perform a full upgrade.
            InsertQuery(Versions, {Versions.key: 'schema_version', Versions.val: 0}).execute()
            database_migrate(db, 0)
        else:
            InsertQuery(Versions, {Versions.key: 'schema_version', Versions.val: db_schema_version}).execute()

    else:
        db_ver = Versions.get(Versions.key == 'schema_version').val

        if db_ver < db_schema_version:
            database_migrate(db, db_ver)

        elif db_ver > db_schema_version:
            log.error("Your database version (%i) appears to be newer than the code supports (%i).",
                      db_ver, db_schema_version)
            log.error("Please upgrade your code base or drop all tables in your database.")
            sys.exit(1)


def database_migrate(db, old_ver):
    # Update database schema version
    Versions.update(val=db_schema_version).where(Versions.key == 'schema_version').execute()

    log.info("Detected database version %i, updating to %i", old_ver, db_schema_version)

    # Perform migrations here
    migrator = None
    if args.db_type == 'mysql':
        migrator = MySQLMigrator(db)
    else:
        migrator = SqliteMigrator(db)

#   No longer necessary, we're doing this at schema 4 as well
#    if old_ver < 1:
#        db.drop_tables([ScannedLocation])

    if old_ver < 2:
        migrate(migrator.add_column('pokestop', 'encounter_id', CharField(max_length=50, null=True)))

    if old_ver < 3:
        migrate(
            migrator.add_column('pokestop', 'active_fort_modifier', CharField(max_length=50, null=True)),
            migrator.drop_column('pokestop', 'encounter_id'),
            migrator.drop_column('pokestop', 'active_pokemon_id')
        )

    if old_ver < 4:
        db.drop_tables([ScannedLocation])

    if old_ver < 5:
        # Some pokemon were added before the 595 bug was "fixed"
        # Clean those up for a better UX
        query = (Pokemon
                 .delete()
                 .where(Pokemon.disappear_time >
                        (datetime.utcnow() - timedelta(hours=24))))
        query.execute()

    if old_ver < 6:
        migrate(
            migrator.add_column('gym', 'last_scanned', DateTimeField(null=True)),
        )

    if old_ver < 7:
        migrate(
            migrator.drop_column('gymdetails', 'description'),
            migrator.add_column('gymdetails', 'description', TextField(null=True, default=""))
        )

    if old_ver < 8:
        # Information in ScannedLocation and Member Status probably already out of date,
        # so drop and re-create

        db.drop_tables([ScannedLocation])
        db.drop_tables([WorkerStatus])

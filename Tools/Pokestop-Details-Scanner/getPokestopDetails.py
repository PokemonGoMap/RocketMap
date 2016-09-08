#!/usr/bin/python
# -*- coding: utf-8 -*-

"""getPokestopDetails.py - get Name/Description/Image for Pokestops from DB."""

from pgoapi import PGoApi
from pgoapi.utilities import f2i
from pgoapi import utilities as util
from pgoapi.exceptions import AuthException
from pgoapi.exceptions import ServerSideRequestThrottlingException
from pgoapi.exceptions import NotLoggedInException
from peewee import *
import time
import sys
import MySQLdb as mdb
import MySQLdb.cursors
import argparse
import pprint


#stolen from utils.py
def parse_unicode(bytestring):
    decoded_string = bytestring.decode(sys.getfilesystemencoding())
    return decoded_string

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--auth-service', type=str.lower, default='ptc',
                    help='Auth Services: ptc or google. Defaults to ptc.')
parser.add_argument('-u', '--username', default='',
                    help='Username.', required=True)
parser.add_argument('-p', '--password', default='',
                    help='Password.', required=True)
parser.add_argument('-l', '--location', type=parse_unicode,
                    help='Location, can be an address or coordinates', required=True)
parser.add_argument('-px', '--proxy', 
                    help='Proxy url (e.g. socks5://127.0.0.1:9050)')
parser.add_argument('--db-type', 
                    help='Type of database to be used (default: mysql)', default='mysql', required=True)
parser.add_argument('-D', '--db', 
                    help='Database filename', default='pogom.db')
                    
parser.add_argument('--db-name', help='Name of the database to be used')
parser.add_argument('--db-user', help='Username for the database')
parser.add_argument('--db-pass', help='Password for the database')
parser.add_argument('--db-host', help='IP or hostname for the database', default='127.0.0.1')
parser.add_argument('--db-port', help='Port for the database', type=int, default=3306)
args = parser.parse_args()
    
position = util.get_pos_by_name(args.location)
if not position:
    print('Location invalid.')
    quit()
        
if args.db_type == 'mysql':
    if not args.db_user or not args.db_pass or not args.db_name:
        print("Needed parameters for MySQL: --db-user, --db-pass, --db-name.")
        quit()
    print('Connecting to MySQL database on {}:{}'.format(args.db_host, args.db_port))
    db = MySQLDatabase(args.db_name, user=args.db_user, password=args.db_pass, host=args.db_host, port=args.db_port)
 
elif args.db_type == 'sqlite':
    if not args.db:
        print("You need to specify an SQLite file with -D / --db.")
        quit()
    db = SqliteDatabase(args.db)
else:
    print("Unsupported database type.")
    quit()    

def run_scan(db, args, position):

    db.connect()
    PokestopDetails.create_table(fail_silently=True)

    pokestops = {}
    pokestops = (Pokestop.select(Pokestop.pokestop_id, Pokestop.latitude, Pokestop.longitude)
                .join(PokestopDetails, JOIN.LEFT_OUTER, on=(PokestopDetails.pokestop_id == Pokestop.pokestop_id))
                .where(
                        (PokestopDetails.name >> None) |
                        (PokestopDetails.name == '')
                      )
                .order_by(Pokestop.latitude, Pokestop.longitude)
                .desc()
                )
                
    api = PGoApi()
    api.set_position(*position)
    
    if args.proxy:
        print("Using proxy {}".format(args.proxy))
        api.set_proxy({'http': args.proxy, 'https': args.proxy}) 
    
    print("Logging in with user {}".format(args.username))
    if not api.login(args.auth_service, args.username, args.password, app_simulation = True):
        return
        
    #test command
    api.get_player()
    time.sleep(0.2)
    

    for stop in pokestops:
        lat = stop.latitude
        lng = stop.longitude
        print("Scanning for Stop at {}, {}".format(lat,lng))
        position = util.get_pos_by_name("{}, {}".format(lat,lng))
        api.set_position(*position)
        cell_ids = util.get_cell_ids(lat, lng)
        timestamps = [0,] * len(cell_ids)
        response_dict = api.get_map_objects(latitude = lat, longitude = lng, since_timestamp_ms = timestamps, cell_id = cell_ids)
        stopinfo = api.fort_details(fort_id = stop.pokestop_id, latitude = lat,  longitude = lng)

        if not stopinfo['responses']:
            print("Got no information, continuing...")
            continue
            
        image = stopinfo['responses']['FORT_DETAILS']['image_urls'][0]
        name = stopinfo['responses']['FORT_DETAILS']['name']
        desc = stopinfo['responses']['FORT_DETAILS'].get('description', '')

        qry = PokestopDetails.insert(pokestop_id=stop.pokestop_id, name=name, image_url=image, description=desc).upsert(upsert=True)
        qry.execute()
        
        time.sleep(1)
        
        

#peewee stuff
class PokestopDetails(Model):
    pokestop_id = CharField(primary_key=True, index=True, max_length=50)
    name = CharField(max_length=100)
    description = TextField(null=True, default="")
    image_url = TextField(null=True, default="")
    class Meta:
        database = db
        
class Pokestop(Model):
    pokestop_id = CharField(primary_key=True, max_length=50)
    enabled = BooleanField()
    latitude = DoubleField()
    longitude = DoubleField()
    last_modified = DateTimeField(index=True)
    lure_expiration = DateTimeField(null=True, index=True)
    active_fort_modifier = CharField(max_length=50, null=True)

    class Meta:
        indexes = ((('latitude', 'longitude'), False),)
        database = db
        
        
run_scan(db, args, position)
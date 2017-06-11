#!/usr/bin/env python

# This script is an example for the 'fake-search-script' option
#
# This script is a companion to 'listener.py' and
# should be run independently of RocketMap.
#
# See 'listener.py' for more details

from multiprocessing.connection import Client
import time
from datetime import datetime, timedelta

print('Waiting for connection...')
connection = Client(('localhost', 7890))
print('...connected')

latitude = 42.7
longitude = -84.5

count = 0
while True:
    time.sleep(3)
    fake_pokemon_objects = [{'pokemon_id': 132,  # ditto
                             'disappear_time': (datetime.utcnow() +
                                                timedelta(seconds=15)),
                             'latitude': latitude,
                             'longitude': longitude + count*.0002}]
    count += 1
    connection.send(fake_pokemon_objects)

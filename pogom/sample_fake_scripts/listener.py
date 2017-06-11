#!/usr/bin/env python

# This script listens for pokemon objects
# from ANOTHER script, independent of RocketMap.
#
# Run THIS script with 'runserver.py', e.g.
#     runserver.py -cf config/config.ini.example -k GMAPS_KEY -l
#         42.7,-84.5 -fss ./pogom/sample_fake_scripts/listener.py
#
# Then, run 'client.py' separately, and the client will
# send data to this script.

from multiprocessing.connection import Listener
import time


def go(args):
    print('waiting for connection...')
    listener = Listener(('', 7890))
    conn = listener.accept()
    print('...connected to ' + str(listener.last_accepted))
    while True:
        time.sleep(3)
        if conn.poll():
            pokemon_objects = conn.recv()
            args.add_pokemon(pokemon_objects)

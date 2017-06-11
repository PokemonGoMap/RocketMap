import random
import imp

from datetime import datetime
from base64 import b64encode
from pogom import utils

from .models import (Pokemon)


def add_fake_pokemon(db_updates_queue, fake_pokemon_objects):
    if not type(fake_pokemon_objects) is list:
        print 'Fake Script: add_fake_pokemon() expects a list'
        print 'instead, got ' + str(fake_pokemon_objects)
        return
    now_date = datetime.utcnow()
    pokemons = {}
    for obj in fake_pokemon_objects:
        error = False
        for key in ['pokemon_id', 'latitude', 'longitude', 'disappear_time']:
            if key not in obj.keys():
                print('fake_pokemon missing "' + key + '"')
                error = True
        if error:
            continue

        fakeid = random.getrandbits(64)
        fakeidstr = str(fakeid).decode('UTF-8')

        time_left_in_seconds = (obj['disappear_time']
                                - now_date).total_seconds()
        message = (utils.get_pokemon_name(obj['pokemon_id']) + ' expires in '
                   + str(time_left_in_seconds/60.) + ' minutes')
        skip_it = time_left_in_seconds <= 0 or time_left_in_seconds > 3600
        if skip_it:
            message += ' (skipping)'
        print(message)
        if skip_it:
            continue

        pokemon = {
            'encounter_id': b64encode(str(fakeid)),
            'spawnpoint_id': fakeidstr,
            'pokemon_id': None,
            'latitude': None,
            'longitude': None,
            'disappear_time': None,
            'individual_attack': None,
            'individual_defense': None,
            'individual_stamina': None,
            'move_1': None,
            'move_2': None,
            'cp': None,
            'height': None,
            'weight': None,
            'gender': None,
            'form': None,
            }

        for key, value in obj.items():
            if key in pokemon:
                pokemon[key] = value
            else:
                print('got unknown fake-pokemon attribute: ' + key)

        pokemons[fakeid] = pokemon

    if pokemons:
        db_updates_queue.put((Pokemon, pokemons))


class FakeSearchScriptArgs:
    pass


def fake_search_thread(args, position, db_updates_queue):
    # pass control to fake_search_script
    add_pokemon_func = (lambda objs: add_fake_pokemon(db_updates_queue, objs))
    script = imp.load_source('', args.fake_search_script)
    fake_search_script_args = FakeSearchScriptArgs()
    fake_search_script_args.args = args
    fake_search_script_args.add_pokemon = add_pokemon_func
    fake_search_script_args.position = position
    script.go(fake_search_script_args)

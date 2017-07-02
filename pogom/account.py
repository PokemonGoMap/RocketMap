#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import time
import random
from threading import Lock
from timeit import default_timer

from pgoapi import PGoApi
from pgoapi.exceptions import AuthException

from .fakePogoApi import FakePogoApi
from .pgoapiwrapper import PGoApiWrapper
from .utils import (in_radius, generate_device_info, equi_rect_distance,
                    clear_dict_response)
from .proxy import get_new_proxy

log = logging.getLogger(__name__)


class TooManyLoginAttempts(Exception):
    pass


class LoginSequenceFail(Exception):
    pass


class NullTimeException(Exception):

    def __init__(self, type):
        self.type = type
        super(NullTimeException, self).__init__(NullTimeException.__name__)


# Create the API object that'll be used to scan.
def setup_api(args, status, account):
    # Create the API instance this will use.
    if args.mock != '':
        api = FakePogoApi(args.mock)
    else:
        identifier = account['username'] + account['password']
        device_info = generate_device_info(identifier)
        api = PGoApiWrapper(PGoApi(device_info=device_info))

    # New account - new proxy.
    if args.proxy:
        # If proxy is not assigned yet or if proxy-rotation is defined
        # - query for new proxy.
        if ((not status['proxy_url']) or
                (args.proxy_rotation != 'none')):

            proxy_num, status['proxy_url'] = get_new_proxy(args)
            if args.proxy_display.upper() != 'FULL':
                status['proxy_display'] = proxy_num
            else:
                status['proxy_display'] = status['proxy_url']

    if status['proxy_url']:
        log.debug('Using proxy %s', status['proxy_url'])
        api.set_proxy({
            'http': status['proxy_url'],
            'https': status['proxy_url']})
        if (status['proxy_url'] not in args.proxy):
            log.warning(
                'Tried replacing proxy %s with a new proxy, but proxy ' +
                'rotation is disabled ("none"). If this isn\'t intentional, ' +
                'enable proxy rotation.',
                status['proxy_url'])

    return api


# Use API to check the login status, and retry the login if possible.
def check_login(args, account, api, position, proxy_url):
    # Logged in? Enough time left? Cool!
    if api._auth_provider and api._auth_provider._ticket_expire:
        remaining_time = api._auth_provider._ticket_expire / 1000 - time.time()

        if remaining_time > 60:
            log.debug(
                'Credentials remain valid for another %f seconds.',
                remaining_time)
            return

    # Try to login. Repeat a few times, but don't get stuck here.
    num_tries = 0

    # One initial try + login_retries.
    while num_tries < (args.login_retries + 1):
        try:
            if proxy_url:
                api.set_authentication(
                    provider=account['auth_service'],
                    username=account['username'],
                    password=account['password'],
                    proxy_config={'http': proxy_url, 'https': proxy_url})
            else:
                api.set_authentication(
                    provider=account['auth_service'],
                    username=account['username'],
                    password=account['password'])
            # Success!
            break
        except AuthException:
            num_tries += 1
            log.error(
                ('Failed to login to Pokemon Go with account %s. ' +
                 'Trying again in %g seconds.'),
                account['username'], args.login_delay)
            time.sleep(args.login_delay)

    if num_tries > args.login_retries:
        log.error(
            ('Failed to login to Pokemon Go with account %s in ' +
             '%d tries. Giving up.'),
            account['username'], num_tries)
        raise TooManyLoginAttempts('Exceeded login attempts.')

    log.debug('Login for account %s successful.', account['username'])
    time.sleep(20)


# Check if all important tutorial steps have been completed.
# API argument needs to be a logged in API instance.
def get_tutorial_state(args, api, account):
    log.debug('Checking tutorial state for %s.', account['username'])
    request = api.create_request()
    request.get_player(
        player_locale=args.player_locale)
    response = request.call(False).get('responses', {})
    if 'GET_PLAYER' not in response:
        return []
    tutorial_state = response['GET_PLAYER'].player_data.tutorial_state
    time.sleep(random.uniform(2, 4))
    return tutorial_state


# Complete minimal tutorial steps.
# API argument needs to be a logged in API instance.
# TODO: Check if game client bundles these requests, or does them separately.
def complete_tutorial(args, api, account, tutorial_state):
    if 0 not in tutorial_state:
        time.sleep(random.uniform(1, 5))
        request = api.create_request()
        request.mark_tutorial_complete(tutorials_completed=0)
        log.debug('Sending 0 tutorials_completed for %s.', account['username'])
        request.call(False)

    if 1 not in tutorial_state:
        time.sleep(random.uniform(5, 12))
        request = api.create_request()
        request.set_avatar(player_avatar={
            'hair': random.randint(1, 5),
            'shirt': random.randint(1, 3),
            'pants': random.randint(1, 2),
            'shoes': random.randint(1, 6),
            'avatar': random.randint(0, 1),
            'eyes': random.randint(1, 4),
            'backpack': random.randint(1, 5)
        })
        log.debug('Sending set random player character request for %s.',
                  account['username'])
        request.call(False)

        time.sleep(random.uniform(0.3, 0.5))

        request = api.create_request()
        request.mark_tutorial_complete(tutorials_completed=1)
        log.debug('Sending 1 tutorials_completed for %s.', account['username'])
        request.call(False)

    time.sleep(random.uniform(0.5, 0.6))
    request = api.create_request()
    request.get_player_profile()
    log.debug('Fetching player profile for %s...', account['username'])
    request.call(False)

    starter_id = None
    if 3 not in tutorial_state:
        time.sleep(random.uniform(1, 1.5))
        request = api.create_request()
        request.get_download_urls(asset_id=[
            '1a3c2816-65fa-4b97-90eb-0b301c064b7a/1477084786906000',
            'aa8f7687-a022-4773-b900-3a8c170e9aea/1477084794890000',
            'e89109b0-9a54-40fe-8431-12f7826c8194/1477084802881000'])
        log.debug('Grabbing some game assets.')
        request.call(False)

        time.sleep(random.uniform(1, 1.6))
        request = api.create_request()
        request.call(False)

        time.sleep(random.uniform(6, 13))
        request = api.create_request()
        starter = random.choice((1, 4, 7))
        request.encounter_tutorial_complete(pokemon_id=starter)
        log.debug('Catching the starter for %s.', account['username'])
        request.call(False)

        time.sleep(random.uniform(0.5, 0.6))
        request = api.create_request()
        request.get_player(player_locale=args.player_locale)
        responses = request.call(False).get('responses', {})

        if 'GET_INVENTORY' in responses:
            for item in (responses['GET_INVENTORY'].inventory_delta
                         .inventory_items):
                pokemon = item.inventory_item_data.pokemon_data
                if pokemon:
                    starter_id = pokemon.id

    if 4 not in tutorial_state:
        time.sleep(random.uniform(5, 12))
        request = api.create_request()
        request.claim_codename(codename=account['username'])
        log.debug('Claiming codename for %s.', account['username'])
        request.call(False)

        time.sleep(random.uniform(1, 1.3))
        request = api.create_request()
        request.mark_tutorial_complete(tutorials_completed=4)
        log.debug('Sending 4 tutorials_completed for %s.', account['username'])
        request.call(False)

        time.sleep(0.1)
        request = api.create_request()
        request.get_player(
            player_locale=args.player_locale)
        request.call(False)

    if 7 not in tutorial_state:
        time.sleep(random.uniform(4, 10))
        request = api.create_request()
        request.mark_tutorial_complete(tutorials_completed=7)
        log.debug('Sending 7 tutorials_completed for %s.', account['username'])
        request.call(False)

    if starter_id:
        time.sleep(random.uniform(3, 5))
        request = api.create_request()
        request.set_buddy_pokemon(pokemon_id=starter_id)
        log.debug('Setting buddy pokemon for %s.', account['username'])
        request.call(False)
        time.sleep(random.uniform(0.8, 1.8))

    # Sleeping before we start scanning to avoid Niantic throttling.
    log.debug('And %s is done. Wait for a second, to avoid throttle.',
              account['username'])
    time.sleep(random.uniform(2, 4))
    return True


# Complete tutorial with a level up by a Pokestop spin.
# API argument needs to be a logged in API instance.
# Called during fort parsing in models.py
def tutorial_pokestop_spin(api, player_level, forts, step_location, account):
    if player_level > 1:
        log.debug(
            'No need to spin a Pokestop. ' +
            'Account %s is already level %d.',
            account['username'], player_level)
    else:  # Account needs to spin a Pokestop for level 2.
        log.debug(
            'Spinning Pokestop for account %s.',
            account['username'])
        for fort in forts:
            if fort.type == 1:
                if spin_pokestop(api, account, fort, step_location):
                    log.debug(
                        'Account %s successfully spun a Pokestop ' +
                        'after completed tutorial.',
                        account['username'])
                    return True

    return False


def get_player_level(map_dict):
    if 'responses' in map_dict and 'GET_INVENTORY' in map_dict['responses']:
        for item in (map_dict['responses']['GET_INVENTORY'].inventory_delta
                     .inventory_items):
            if item.inventory_item_data.HasField("player_stats"):
                return item.inventory_item_data.player_stats.level

    return 0


def get_inventory_items(map_dict):
    inventory_items_response = map_dict['responses'][
        'GET_INVENTORY']['inventory_delta']['inventory_items']

    inventory_items = []
    if len(inventory_items_response) > 0:
        inventory_items = ([item['inventory_item_data']['item']
                           for item in inventory_items_response
                           if 'item' in item.get('inventory_item_data', {})])

        if len(inventory_items) > 0:
            return inventory_items

    return False


def spin_pokestop(api, account, fort, step_location):
    spinning_radius = 0.04
    if in_radius((fort.latitude, fort.longitude), step_location,
                 spinning_radius):
        log.debug('Attempt to spin Pokestop (ID %s).', fort.id)

        time.sleep(random.uniform(0.8, 1.8))  # Do not let Niantic throttle
        response = spin_pokestop_request(api, account, fort, step_location)
        time.sleep(random.uniform(2, 4))  # Don't let Niantic throttle.

        # Check for reCaptcha
        captcha_url = response['responses']['CHECK_CHALLENGE'][
            'challenge_url']
        if len(captcha_url) > 1:
            log.debug('Account encountered a reCaptcha.')
            return False

        spin_result = response['responses']['FORT_SEARCH'].result
        if spin_result is 1:
            log.debug('Successful Pokestop spin.')
            return True
        elif spin_result is 2:
            log.debug('Pokestop was not in range to spin.')
        elif spin_result is 3:
            log.debug('Failed to spin Pokestop. Has recently been spun.')
        elif spin_result is 4:
            log.debug('Failed to spin Pokestop. Inventory is full.')
        elif spin_result is 5:
            log.debug('Maximum number of Pokestops spun for this day.')
        else:
            log.debug(
                'Failed to spin a Pokestop. Unknown result %d.',
                spin_result)

    return False


def spin_pokestop_request(api, account, fort, step_location):
    try:
        req = api.create_request()
        req.fort_search(
            fort_id=fort.id,
            fort_latitude=fort.latitude,
            fort_longitude=fort.longitude,
            player_latitude=step_location[0],
            player_longitude=step_location[1])
        req.check_challenge()
        req.get_hatched_eggs()
        req.get_inventory()
        req.check_awarded_badges()
        req.get_buddy_walked()
        req.get_inbox(is_history=True)
        spin_pokestop_response = req.call()

        return spin_pokestop_response

    except Exception as e:
        log.error('Exception while spinning Pokestop: %s.', repr(e))
        return False


def encounter_pokemon_request(api, account, encounter_id, spawnpoint_id,
                              scan_location):
    try:
        # Setup encounter request envelope.
        req = api.create_request()
        req.encounter(
            encounter_id=encounter_id,
            spawn_point_id=spawnpoint_id,
            player_latitude=scan_location[0],
            player_longitude=scan_location[1])
        req.check_challenge()
        req.get_hatched_eggs()
        req.get_inventory(last_timestamp_ms=account['last_timestamp_ms'])
        req.check_awarded_badges()
        req.get_buddy_walked()
        req.get_inbox(is_history=True)
        response = req.call()
        parse_new_timestamp_ms(account, response)
        return response
    except Exception as e:
        log.exception('Exception while encountering Pokémon: %s.', repr(e))
        return False


def parse_download_settings(account, api_response):
    if 'DOWNLOAD_REMOTE_CONFIG_VERSION' in api_response['responses']:
        remote_config = (api_response['responses']
                         .get('DOWNLOAD_REMOTE_CONFIG_VERSION'))

        # We're accessing a protobuf. Keys will always exist, but if they're
        # empty, they will return 0.
        asset_time = remote_config.asset_digest_timestamp_ms / 1000000
        template_time = remote_config.item_templates_timestamp_ms / 1000

        if asset_time == 0 or asset_time is None:
            raise NullTimeException(type="asset")
        if template_time == 0 or template_time is None:
            raise NullTimeException(type="template")

        download_settings = {}
        download_settings['hash'] = api_response['responses'][
            'DOWNLOAD_SETTINGS'].hash
        download_settings['asset_time'] = asset_time
        download_settings['template_time'] = template_time

        account['remote_config'] = download_settings

        log.debug('Download settings for account %s: %s.',
                  account['username'],
                  download_settings)
        return True


# Parse new timestamp from the GET_INVENTORY response.
def parse_new_timestamp_ms(account, api_response):
    if 'GET_INVENTORY' in api_response['responses']:
        account['last_timestamp_ms'] = (api_response['responses'][
            'GET_INVENTORY'].inventory_delta.new_timestamp_ms)

        player_level = get_player_level(api_response)
        if player_level:
            account['level'] = player_level


# The AccountSet returns a scheduler that cycles through different
# sets of accounts (e.g. L30). Each set is defined at runtime, and is
# (currently) used to separate regular accounts from L30 accounts.
# TODO: Migrate the old account Queue to a real AccountScheduler, preferably
# handled globally via database instead of per instance.
# TODO: Accounts in the AccountSet are exempt from things like the
# account recycler thread. We could've hardcoded support into it, but that
# would have added to the amount of ugly code. Instead, we keep it as is
# until we have a proper account manager.
class AccountSet(object):

    def __init__(self, kph):
        self.sets = {}

        # Scanning limits.
        self.kph = kph

        # Thread safety.
        self.next_lock = Lock()

    # Set manipulation.
    def create_set(self, name, values=None):
        if values is None:
            values = []
        if name in self.sets:
            raise Exception('Account set ' + name + ' is being created twice.')

        self.sets[name] = values

    # Release an account back to the pool after it was used.
    def release(self, account):
        if 'in_use' not in account:
            log.error('Released account %s back to the AccountSet,'
                      + " but it wasn't locked.",
                      account['username'])
        else:
            account['in_use'] = False

    # Get next account that is ready to be used for scanning.
    def next(self, set_name, coords_to_scan):
        # Yay for thread safety.
        with self.next_lock:
            # Readability.
            account_set = self.sets[set_name]

            # Loop all accounts for a good one.
            now = default_timer()
            max_speed_kmph = self.kph

            for i in range(len(account_set)):
                account = account_set[i]

                # Make sure it's not in use.
                if account.get('in_use', False):
                    continue

                # Make sure it's not captcha'd.
                if account.get('captcha', False):
                    continue

                # Check if we're below speed limit for account.
                last_scanned = account.get('last_scanned', False)

                if last_scanned:
                    seconds_passed = now - last_scanned
                    old_coords = account.get('last_coords', coords_to_scan)

                    distance_km = equi_rect_distance(
                        old_coords,
                        coords_to_scan)
                    cooldown_time_sec = distance_km / max_speed_kmph * 3600

                    # Not enough time has passed for this one.
                    if seconds_passed < cooldown_time_sec:
                        continue

                # We've found an account that's ready.
                account['last_scanned'] = now
                account['last_coords'] = coords_to_scan
                account['in_use'] = True

                return account

        # TODO: Instead of returning False, return the amount of min. seconds
        # the instance needs to wait until the first account becomes available,
        # so it doesn't need to keep asking if we know we need to wait.
        return False


# Check if Pokestop is spinnable and not on cooldown.
def pokestop_spinnable(fort, step_location):
    spinning_radius = 0.038  # Maximum distance to spin Pokestops.
    in_range = in_radius((fort['latitude'], fort['longitude']), step_location,
                         spinning_radius)
    now = time.time()
    pause_needed = 'cooldown_complete_timestamp_ms' in fort and fort[
        'cooldown_complete_timestamp_ms'] / 1000 > now
    return in_range and not pause_needed


# 50% Chance to spin a Pokestop.
def spinning_try(api, fort, step_location, account, map_dict, args):
    if account['hour_spins'] > args.account_max_spins:
        log.info('Account %s has reached its Pokestop spinning limits.',
                 account['username'])
        return False

    # Set 50% Chance to spin a Pokestop.
    if random.randint(0, 100) < 50:
        time.sleep(random.uniform(2, 4))  # Do not let Niantic throttle.
        spin_response = spin_pokestop_request(api, fort, step_location)
        if not spin_response:
            return False

        # Check for reCaptcha
        captcha_url = spin_response['responses']['CHECK_CHALLENGE'][
            'challenge_url']
        if len(captcha_url) > 1:
            log.debug('Account encountered a reCaptcha.')
            return False

        # Catch all possible responses.
        spin_result = spin_response['responses']['FORT_SEARCH']['result']
        if spin_result is 1:
            log.info('Successful Pokestop spin with %s.', account['username'])
            # Update account stats and clear inventory if necessary.
            parse_inventory(api, account, map_dict)
            parse_level_up_rewards(api, account, map_dict)
            clear_inventory(api, account)
            account['session_spins'] += 1
            incubate_eggs(api, account)
            return True
        # Catch all other results.
        elif spin_result is 2:
            log.info('Pokestop %s was not in range to spin for account' +
                     '%s', fort['id'], account['username'])
        elif spin_result is 3:
            log.info('Failed to spin Pokestop %s. %s Has recently spun this' +
                     'stop.', fort['id'], account['username'])
        elif spin_result is 4:
            log.info('Failed to spin Pokestop %s. %s Inventory is full.',
                     fort['id'], account['username'])
            log.info('Clearing Inventory...')
            clear_inventory(api, account)
        elif spin_result is 5:
            log.warning('Account %s has spun maximum Pokestops for today.',
                        account['username'])
        else:
            log.info('Failed to spin a Pokestop with account %s .' +
                     'Unknown result %d.', account['username'], spin_result)
    return False


# Parse player stats and inventory into account.
def parse_inventory(api, account, map_dict):
    inventory = map_dict['responses'][
        'GET_INVENTORY']['inventory_delta']['inventory_items']
    parsed_items = 0
    parsed_pokemons = 0
    parsed_eggs = 0
    parsed_incubators = 0
    account['incubators'] = []
    account['eggs'] = []
    for item in inventory:
        item_data = item.get('inventory_item_data', {})
        if 'player_stats' in item_data:
            stats = item_data['player_stats']
            account['level'] = stats['level']
            account['spins'] = stats.get('poke_stop_visits', 0)
            account['walked'] = stats.get('km_walked', 0)

            log.info('Parsed %s player stats: level %d, %f km ' +
                     'walked, %d spins.', account['username'],
                     account['level'], account['walked'], account['spins'])
        elif 'item' in item_data:
            item_id = item_data['item']['item_id']
            item_count = item_data['item'].get('count', 0)
            account['items'][item_id] = item_count
            parsed_items += item_count
        elif 'egg_incubators' in item_data:
            incubators = item_data['egg_incubators']['egg_incubator']
            for incubator in incubators:
                if incubator.get('pokemon_id', 0):
                    left = (incubator['target_km_walked']
                            - account['walked'])
                    log.debug('Egg kms remaining: %.2f', left)
                else:
                    account['incubators'].append({
                        'id': incubator['id'],
                        'item_id': incubator['item_id'],
                        'uses_remaining': incubator.get('uses_remaining', 0),
                    })
                    parsed_incubators += 1
        elif ('pokemon_data' in item_data and
              item_data['pokemon_data'].get('id', 0)):
            p_data = item_data['pokemon_data']
            p_id = p_data.get('id', 0)
            if not p_data.get('is_egg', False):
                account['pokemons'][p_id] = {
                    'pokemon_id': p_data.get('pokemon_id', 0),
                    'move_1': p_data['move_1'],
                    'move_2': p_data['move_2'],
                    'height': p_data['height_m'],
                    'weight': p_data['weight_kg'],
                    'gender': p_data['pokemon_display']['gender'],
                    'cp': p_data['cp'],
                    'cp_multiplier': p_data['cp_multiplier']
                }
                parsed_pokemons += 1
            else:
                if p_data.get('egg_incubator_id', None):
                    # Egg is already incubating.
                    continue
                account['eggs'].append({
                    'id': p_id,
                    'km_target': p_data['egg_km_walked_target']
                })
                parsed_eggs += 1
    log.info(
        'Parsed %s player inventory: %d items, %d pokemons, %d available ' +
        'eggs and %d available incubators.',
        account['username'], parsed_items, parsed_pokemons, parsed_eggs,
        parsed_incubators)


def reset_account(account):
    account['start_time'] = time.time()
    account['items'] = {}
    account['pokemons'] = {}
    account['incubators'] = []
    account['eggs'] = []
    account['level'] = 0
    account['spins'] = 0
    account['session_spins'] = 0
    account['hour_spins'] = 0
    account['walked'] = 0.0


def cleanup_account_stats(account):
    elapsed_time = time.time() - account['start_time']

    # Just to prevent division by 0 errors, when needed
    # set elapsed to 1 millisecond
    if elapsed_time == 0:
        elapsed_time = 1

    spins_h = account['session_spins'] * 3600.0 / elapsed_time
    account['hour_spins'] = spins_h


def clear_inventory(api, account):
    items = [(1, 'Pokeball'), (2, 'Greatball'), (3, 'Ultraball'),
             (101, 'Potion'), (102, 'Super Potion'), (103, 'Hyper Potion'),
             (104, 'Max Potion'),
             (201, 'Revive'), (202, 'Max Revive'),
             (701, 'Razz Berry'), (703, 'Nanab Berry'), (705, 'Pinap Berry'),
             (1101, 'Sun Stone'), (1102, 'Kings Rock'), (1103, 'Metal Coat'),
             (1104, 'Dragon Scale'), (1105, 'Upgrade')]

    release_ids = []
    total_pokemon = len(account['pokemons'])
    release_count = int(total_pokemon - 5)
    if total_pokemon > random.randint(5, 10):
        release_ids = random.sample(account['pokemons'].keys(), release_count)
        # Do not let Niantic throttle
        time.sleep(random.uniform(2, 4))
        release_p_response = request_release_pokemon(api, account, 0,
                                                     release_ids)

        captcha_url = release_p_response['responses']['CHECK_CHALLENGE'][
            'challenge_url']
        if len(captcha_url) > 1:
            log.info('Account encountered a reCaptcha.')
            return False

        release_response = release_p_response['responses']['RELEASE_POKEMON']
        release_result = release_response['result']

        if release_result is 1:
            log.info('Sucessfully Released %s Pokemon', len(release_ids))
            for p_id in release_ids:
                account['pokemons'].pop(p_id, None)
        elif release_result != 1:
            log.error('Failed to release Pokemon.')

    for item_id, item_name in items:
        item_count = account['items'].get(item_id, 0)
        random_max = random.randint(5, 10)
        if item_count > random_max:
            drop_count = item_count - random_max

            # Do not let Niantic throttle
            time.sleep(random.uniform(2, 4))
            clear_inventory_response = clear_inventory_request(
                api, item_id, drop_count)

            captcha_url = clear_inventory_response['responses'][
                'CHECK_CHALLENGE']['challenge_url']
            if len(captcha_url) > 1:
                log.info('Account encountered a reCaptcha.')
                return False

            clear_response = clear_inventory_response[
                'responses']['RECYCLE_INVENTORY_ITEM']
            clear_result = clear_response['result']
            if clear_result is 1:
                log.info('Clearing %s %ss succeeded.', item_count,
                         item_name)
            elif clear_result is 2:
                log.debug('Not enough items to clear, parsing failed.')
            elif clear_result is 3:
                log.debug('Tried to recycle incubator, parsing failed.')
            else:
                log.warning('Failed to clear inventory.')

            log.debug('Recycled inventory: \n\r{}'.format(clear_result))

    return


def incubate_eggs(api, account):
    log.debug('Available incubators %d.', len(account['incubators']))
    account['eggs'] = sorted(account['eggs'], key=lambda k: k['km_target'])
    for incubator in account['incubators']:
        if not account['eggs']:
            log.debug('Account %s has no eggs to incubate.',
                      account['username'])
            break
        egg = account['eggs'].pop(0)
        time.sleep(random.uniform(2.0, 4.0))
        if request_use_item_egg_incubator(
           api, account, incubator['id'], egg['id']):
            log.info('Egg #%s (%.0f km) is on incubator #%s.',
                     egg['id'], egg['km_target'], incubator['id'])
            account['incubators'].remove(incubator)
        else:
            log.error('Failed to put egg on incubator #%s.', incubator['id'])

    return


def clear_inventory_request(api, item_id, drop_count):
    try:
        req = api.create_request()
        req.recycle_inventory_item(item_id=item_id, count=drop_count)
        req.check_challenge()
        req.get_hatched_eggs()
        req.get_inventory()
        req.check_awarded_badges()
        req.get_buddy_walked()
        req.get_inbox(is_history=True)
        clear_inventory_response = req.call()

        return clear_inventory_response

    except Exception as e:
        log.warning('Exception while clearing Inventory: %s', repr(e))
        return False


def request_use_item_egg_incubator(api, account, incubator_id, egg_id):
    try:
        req = api.create_request()
        req.use_item_egg_incubator(
            item_id=incubator_id,
            pokemon_id=egg_id
        )
        req.check_challenge()
        req.get_hatched_eggs()
        req.get_inventory()
        req.check_awarded_badges()
        req.get_buddy_walked()
        req.get_inbox(is_history=True)
        req.call()
        return True

    except Exception as e:
        log.warning('Exception while putting an egg in incubator: %s', repr(e))
    return False


def parse_level_up_rewards(api, account, map_dict):
    try:
        req = api.create_request()
        req.level_up_rewards(level=account['level'])
        req.check_challenge()
        req.get_hatched_eggs()
        req.get_inventory()
        req.check_awarded_badges()
        req.download_settings()
        req.get_buddy_walked()
        req.get_inbox(is_history=True)
        response = req.call()

        return response

    except Exception as e:
        log.error('Exception while getting Level Up Rewards: %s', repr(e))

    rewards = response['responses']['LEVEL_UP_REWARDS']['result']
    if rewards is 1:
        log.info('Account %s collected its level up rewards.',
                 account['username'])
        # Parse item rewards into account inventory.
        parse_inventory(api, account, map_dict)
        return True
    elif rewards != 1:
        log.info('Account %s already collected its level up rewards.',
                 account['username'])


def request_release_pokemon(api, account, pokemon_id, release_ids=[]):
    try:
        req = api.create_request()
        req.release_pokemon(pokemon_id=pokemon_id,
                            pokemon_ids=release_ids)
        req.check_challenge()
        req.get_hatched_eggs()
        req.get_inventory()
        req.check_awarded_badges()
        req.get_buddy_walked()
        req.get_inbox(is_history=True)
        release_p_response = req.call()

        return release_p_response

    except Exception as e:
        log.error('Exception while releasing Pokemon: %s', repr(e))

    return False

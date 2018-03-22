#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import time
import random

from pgoapi import PGoApi
from pgoapi.exceptions import AuthException

from .fakePogoApi import FakePogoApi
from .pgoapiwrapper import PGoApiWrapper
from .utils import in_radius, generate_device_info
from .proxy import get_new_proxy

from .apiRequests import (send_generic_request, fort_details,
                          recycle_inventory_item, use_item_egg_incubator,
                          release_pokemon, level_up_rewards, fort_search,
                          AccountBannedException)

log = logging.getLogger(__name__)


# Keep track of different types of bans using a single field.
class AccountBanned:
    Clear = 0
    Shadowban = 1
    Temporary = 2
    Permanent = 3


# Create the API object that'll be used to scan.
def setup_api(args, status, account):
    reset_account(account)
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
def check_login(account_manager, status, api, account):
    # Logged in? Enough time left? Cool!
    if api._auth_provider and api._auth_provider._access_token:
        remaining_time = api._auth_provider._access_token_expiry - time.time()

        if remaining_time > 60:
            log.debug(
                'Credentials remain valid for another %f seconds.',
                remaining_time)
            return True

    # Try to login. Repeat a few times, but don't get stuck here.
    status['message'] = 'Logging in Pokemon Go with account {}...'.format(
        account['username'])
    log.info(status['message'])
    num_tries = 0
    login_delay = account_manager.args.login_delay
    login_retries = account_manager.args.login_retries
    proxy_url = status['proxy_url']

    # One initial try + login_retries.
    while num_tries < (login_retries + 1):
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
            status['message'] = (
                'Failed attempt #{} to login to Pokemon Go with account {}. ' +
                'Trying again in {} seconds.').format(
                    num_tries, account['username'], login_delay)
            log.error(status['message'])
            time.sleep(login_delay)

    if num_tries > login_retries:
        account['failed'] += 1
        failed_count = num_tries * account['failed']
        if account['failed'] < account_manager.args.account_max_failures:
            status['message'] = (
                'Unable to login to Pokemon Go with account {}. ' +
                'Failed {} login attempts on {} separate occasions.').format(
                    account['username'], failed_count, account['failed'])

            account_manager.failed_account(account, 'login')
        else:
            status['message'] = (
                'Account {} assumed permanently banned. ' +
                'Failed {} login attempts on {} separate occasions.').format(
                    account['username'], failed_count, account['failed'])

            account['banned'] = AccountBanned.Permanent
            account_manager.failed_account(account, 'permanent ban')

        log.error(status['message'])
        return False

    account['failed'] = 0
    time.sleep(random.uniform(2, 4))

    # Simulate login sequence.
    if not rpc_login_sequence(account_manager, status, api, account):
        fail_reason = 'exception'
        if account['banned'] == AccountBanned.Temporary:
            fail_reason = 'temporary ban'

        account_manager.failed_account(account, fail_reason)
        return False

    return True


# Simulate real app via login sequence.
def rpc_login_sequence(account_manager, status, api, account):
    total_req = 0
    app_version = PGoApi.get_api_version()

    # 1 - Make an empty request to mimick real app behavior.
    log.debug('Starting RPC login sequence...')

    try:
        req = api.create_request()
        req.call(False)

        total_req += 1
        time.sleep(random.uniform(.43, .97))
    except Exception as e:
        log.exception('Login sequence for account %s failed. ' +
                      'Exception in call request: %s.',
                      account['username'], e)

        status['message'] = (
            'Account {} failed RPC login sequence step #1.').format(
                account['username'])
        return False

    # 2 - Get player information.
    log.debug('Fetching player information...')

    try:
        req = api.create_request()
        req.get_player(player_locale=account_manager.args.player_locale)
        resp = req.call(False)
        parse_get_player(account, resp)

        total_req += 1
        time.sleep(random.uniform(.53, 1.1))
        if account['warning']:
            log.warning('Account %s has received a warning.',
                        account['username'])
    except Exception as e:
        log.exception('Login sequence for account %s failed. ' +
                      'Exception in player request: %s.',
                      account['username'], e)

        status['message'] = (
            'Account {} failed RPC login sequence step #2.').format(
                account['username'])
        return False

    # 3 - Get remote config version.
    log.debug('Downloading remote config version...')
    try:
        req = api.create_request()
        req.download_remote_config_version(
            platform=1,
            device_model=api.device_info['device_model_boot'],
            app_version=app_version)
        send_generic_request(
            req, account, settings=True, buddy=False, inbox=False)

        total_req += 1
        time.sleep(random.uniform(.53, 1.1))
    except AccountBannedException as e:
        status['message'] = (
            'Account {} is temporarily banned.').format(account['username'])
        log.error(status['message'])
        account['banned'] = AccountBanned.Temporary

        return False
    except Exception as e:
        log.exception('Login sequence for account %s failed. ' +
                      'Exception downloading remote config: %s.',
                      account['username'], e)

        status['message'] = (
            'Account {} failed RPC login sequence step #3.').format(
                account['username'])
        return False

    remote_config = account.get('remote_config', {})

    # 4 - Get asset digest.
    if remote_config.get('asset_time', 0) <= account['time_assets']:
        log.debug('Skipped fetching asset digest.')
    else:
        log.debug('Fetching asset digest...')
        i = random.randint(0, 3)
        req_count = 0
        result = 2
        page_offset = 0
        page_timestamp = 0

        time.sleep(random.uniform(.7, 1.2))

        while result == 2:
            req = api.create_request()
            req.get_asset_digest(
                platform=1,
                app_version=app_version,
                paginate=True,
                page_offset=page_offset,
                page_timestamp=page_timestamp)
            resp = send_generic_request(req, account, settings=True,
                                        buddy=False, inbox=False)

            req_count += 1
            total_req += 1

            if i > 2:
                time.sleep(random.uniform(1.4, 1.6))
                i = 0
            else:
                i += 1
                time.sleep(random.uniform(.3, .5))

            try:
                # Re-use variable name. Also helps GC.
                resp = resp['responses']['GET_ASSET_DIGEST']
            except KeyError:
                break

            result = resp.result
            page_offset = resp.page_offset
            page_timestamp = resp.timestamp_ms
            log.debug('Completed %d requests to get asset digest.',
                      req_count)

    # 5 - Get item templates.
    if remote_config.get('template_time', 0) <= account['time_templates']:
        log.debug('Skipped fetching item templates.')
    else:
        log.debug('Fetching item templates...')
        i = random.randint(0, 3)
        req_count = 0
        result = 2
        page_offset = 0
        page_timestamp = 0

        while result == 2:
            req = api.create_request()
            req.download_item_templates(
                paginate=True,
                page_offset=page_offset,
                page_timestamp=page_timestamp)
            resp = send_generic_request(req, account, settings=True,
                                        buddy=False, inbox=False)

            req_count += 1
            total_req += 1

            if i > 2:
                time.sleep(random.uniform(1.4, 1.6))
                i = 0
            else:
                i += 1
                time.sleep(random.uniform(.25, .5))

            try:
                # Re-use variable name. Also helps GC.
                resp = resp['responses']['DOWNLOAD_ITEM_TEMPLATES']
            except KeyError:
                break

            result = resp.result
            page_offset = resp.page_offset
            page_timestamp = resp.timestamp_ms
            log.debug('Completed %d requests to download'
                      + ' item templates.', req_count)

    # Check tutorial completion.
    if not all(x in account['tutorials'] for x in (0, 1, 3, 4, 7)):
        status['message'] = (
            'Completing tutorial steps for {}.').format(account['username'])
        log.info(status['message'])
        complete_tutorial(api, account, account_manager.args.player_locale)
    else:
        log.debug('Account %s already did the tutorials.', account['username'])
        # 6 - Get player profile.
        log.debug('Fetching player profile...')
        try:
            req = api.create_request()
            req.get_player_profile()
            send_generic_request(req, account, settings=True, inbox=False)
            total_req += 1
            time.sleep(random.uniform(.2, .3))
        except Exception as e:
            log.exception('Login sequence for account %s failed. ' +
                          'Exception getting player profile: %s.',
                          account['username'], e)

            status['message'] = (
                'Account {} failed RPC login sequence step #6.').format(
                    account['username'])
            return False

    # 7 - Make an empty request to retrieve store items.
    log.debug('Retrieving Store Items...')
    try:
        req = api.create_request()
        req.get_store_items()
        req.call(False)

        total_req += 1
        time.sleep(random.uniform(.6, 1.1))
    except Exception as e:
        log.exception('Login sequence for account %s failed. ' +
                      'Exception retrieving store items: %s.',
                      account['username'], e)

        status['message'] = (
            'Account {} failed RPC login sequence step #7.').format(
                account['username'])
        return False

    # 8 - Make an empty request to fetch all News.
    log.debug('Fetching News...')
    try:
        req = api.create_request()
        req.fetch_all_news()
        send_generic_request(req, account, settings=True)

        total_req += 1
        time.sleep(random.uniform(.45, .7))
    except Exception as e:
        log.exception('Login sequence for account %s failed. ' +
                      'Exception fetching all news: %s.',
                      account['username'], e)

        status['message'] = (
            'Account {} failed RPC login sequence step #8.').format(
                account['username'])
        return False

    # 9 - Check if there are level up rewards to claim.
    log.debug('Checking if there are level up rewards to claim...')
    try:
        req = api.create_request()
        req.level_up_rewards(level=account['level'])
        send_generic_request(req, account, settings=True)

        total_req += 1
        time.sleep(random.uniform(.45, .7))
    except Exception as e:
        log.exception('Login sequence for account %s failed. ' +
                      'Exception fetching level-up rewards: %s.',
                      account['username'], e)

        status['message'] = (
            'Account {} failed RPC login sequence step #9.').format(
                account['username'])
        return False

    status['message'] = (
            'Login RPC sequence for {} successful with {} requests.'.format(
                account['username'], total_req))
    log.info(status['message'])

    time.sleep(random.uniform(3, 5))

    if account['buddy'] == 0 and len(account['pokemons']) > 0:
        poke_id = random.choice(account['pokemons'].keys())
        req = api.create_request()
        req.set_buddy_pokemon(pokemon_id=poke_id)
        log.debug('Setting buddy pokemon for %s.', account['username'])
        send_generic_request(req, account)

    time.sleep(random.uniform(10, 20))
    return True


# Complete minimal tutorial steps.
# API argument needs to be a logged in API instance.
# TODO: Check if game client bundles these requests, or does them separately.
def complete_tutorial(api, account, player_locale):
    tutorial_state = account['tutorials']
    if 0 not in tutorial_state:
        time.sleep(random.uniform(1, 5))
        req = api.create_request()
        req.mark_tutorial_complete(tutorials_completed=0)
        log.debug('Sending 0 tutorials_completed for %s.', account['username'])
        send_generic_request(req, account, buddy=False, inbox=False)

        time.sleep(random.uniform(0.5, 0.6))
        req = api.create_request()
        req.get_player(player_locale=player_locale)
        send_generic_request(req, account, buddy=False, inbox=False)

    if 1 not in tutorial_state:
        time.sleep(random.uniform(5, 12))
        req = api.create_request()
        req.set_avatar(player_avatar={
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
        send_generic_request(req, account, buddy=False, inbox=False)

        time.sleep(random.uniform(0.3, 0.5))
        req = api.create_request()
        req.mark_tutorial_complete(tutorials_completed=1)
        log.debug('Sending 1 tutorials_completed for %s.', account['username'])
        send_generic_request(req, account, buddy=False, inbox=False)

        time.sleep(random.uniform(0.5, 0.6))
        req = api.create_request()
        req.get_player_profile()
        log.debug('Fetching player profile for %s...', account['username'])
        send_generic_request(req, account, inbox=False)

    if 3 not in tutorial_state:
        time.sleep(random.uniform(1, 1.5))
        req = api.create_request()
        req.get_download_urls(asset_id=[
            '1a3c2816-65fa-4b97-90eb-0b301c064b7a/1477084786906000',
            'aa8f7687-a022-4773-b900-3a8c170e9aea/1477084794890000',
            'e89109b0-9a54-40fe-8431-12f7826c8194/1477084802881000'])
        log.debug('Grabbing some game assets.')
        send_generic_request(req, account, inbox=False)

        time.sleep(random.uniform(6, 13))
        req = api.create_request()
        starter = random.choice((1, 4, 7))
        req.encounter_tutorial_complete(pokemon_id=starter)
        log.debug('Catching the starter for %s.', account['username'])
        send_generic_request(req, account, inbox=False)

        time.sleep(random.uniform(0.5, 0.6))
        req = api.create_request()
        req.get_player(player_locale=player_locale)
        send_generic_request(req, account, inbox=False)

    if 4 not in tutorial_state:
        time.sleep(random.uniform(5, 12))
        req = api.create_request()
        req.claim_codename(codename=account['username'])
        log.debug('Claiming codename for %s.', account['username'])
        send_generic_request(req, account, inbox=False)

        time.sleep(0.1)
        req = api.create_request()
        req.get_player(player_locale=player_locale)
        send_generic_request(req, account, inbox=False)

        time.sleep(random.uniform(1, 1.3))
        req = api.create_request()
        req.mark_tutorial_complete(tutorials_completed=4)
        log.debug('Sending 4 tutorials_completed for %s.', account['username'])
        send_generic_request(req, account, inbox=False)

    if 7 not in tutorial_state:
        time.sleep(random.uniform(4, 10))
        req = api.create_request()
        req.mark_tutorial_complete(tutorials_completed=7)
        log.debug('Sending 7 tutorials_completed for %s.', account['username'])
        send_generic_request(req, account, inbox=False)

    # Sleeping before we start scanning to avoid Niantic throttling.
    log.debug('And %s is done. Wait for a second, to avoid throttle.',
              account['username'])
    time.sleep(random.uniform(2, 4))
    return True


def reset_account(account):
    account['start_time'] = time.time()
    account['tutorials'] = []
    account['items'] = {}
    account['pokemons'] = {}
    account['incubators'] = []
    account['eggs'] = []
    account['spins'] = 0
    account['session_spins'] = 0
    account['walked'] = 0.0
    account['last_timestamp_ms'] = 0


def can_spin(account, max_h_spins):
    elapsed_time = time.time() - account['start_time']

    # Just to prevent division by 0 errors, when needed
    # set elapsed to 1 millisecond.
    if elapsed_time == 0:
        elapsed_time = 1

    return (account['session_spins'] * 3600.0 / elapsed_time) <= max_h_spins


# Check if Pokestop is spinnable and not on cooldown.
def pokestop_spinnable(fort, step_location):
    if not fort.enabled:
        return False

    spinning_radius = 38
    in_range = in_radius((fort.latitude, fort.longitude),
                         step_location, spinning_radius)
    now = time.time()
    pause_needed = fort.cooldown_complete_timestamp_ms / 1000 > now
    return in_range and not pause_needed


def spin_pokestop(account_manager, status, api, account, fort):
    if not can_spin(account, account_manager.args.account_max_spins):
        log.warning('Account %s has reached its Pokestop spinning limits.',
                    account['username'])
        return False
    # Set 50% Chance to spin a Pokestop.
    if random.random() > 0.5 or account['level'] == 1:
        location = (account['latitude'], account['longitude'])
        time.sleep(random.uniform(0.8, 1.8))
        fort_details(api, account, fort)
        time.sleep(random.uniform(0.8, 1.8))  # Don't let Niantic throttle.
        response = fort_search(api, account, fort, location)
        time.sleep(random.uniform(2, 4))  # Don't let Niantic throttle.

        # Check for reCaptcha.
        captcha = account_manager.handle_captcha(
            account, status, api, response)
        if captcha['found'] and captcha['failed']:
            # Note: Account was removed from rotation.
            return False
        elif captcha['found']:
            # Make another fort search request.
            response = fort_search(api, account, fort, location)

        if not response or 'FORT_SEARCH' not in response['responses']:
            log.error('Failed to spin a Pokestop.')
            return False

        spin_result = response['responses']['FORT_SEARCH'].result
        if spin_result == 1:
            log.info('Successful Pokestop spin with %s.', account['username'])
            # Update account stats and clear inventory if necessary.
            parse_level_up_rewards(api, account)
            clear_inventory(account_manager, status, api, account)
            account['session_spins'] += 1
            incubate_eggs(api, account)
            return True
        elif spin_result == 2:
            log.debug('Pokestop was not in range to spin.')
        elif spin_result == 3:
            log.debug('Failed to spin Pokestop. Has recently been spun.')
        elif spin_result == 4:
            log.debug('Failed to spin Pokestop. Inventory is full.')
            clear_inventory(account_manager, status, api, account)
        elif spin_result == 5:
            log.debug('Maximum number of Pokestops spun for this day.')
        else:
            log.error('Failed to spin a Pokestop. Unknown result %d.',
                      spin_result)

    return False


def parse_get_player(account, api_response):
    if 'GET_PLAYER' in api_response['responses']:
        player_data = api_response['responses']['GET_PLAYER'].player_data

        account['warning'] = api_response['responses']['GET_PLAYER'].warn
        account['tutorials'] = player_data.tutorial_state
        account['buddy'] = player_data.buddy_pokemon.id


def clear_inventory(account_manager, status, api, account):
    items = [(1, 'Pokeball'), (2, 'Greatball'), (3, 'Ultraball'),
             (101, 'Potion'), (102, 'Super Potion'), (103, 'Hyper Potion'),
             (104, 'Max Potion'),
             (201, 'Revive'), (202, 'Max Revive'),
             (701, 'Razz Berry'), (703, 'Nanab Berry'), (705, 'Pinap Berry'),
             (1101, 'Sun Stone'), (1102, 'Kings Rock'), (1103, 'Metal Coat'),
             (1104, 'Dragon Scale'), (1105, 'Upgrade')]

    total_pokemon = len(account['pokemons'])
    release_count = int(total_pokemon - 5)
    if total_pokemon > random.randint(5, 10):
        release_ids = random.sample(account['pokemons'].keys(), release_count)
        if account['buddy'] in release_ids:
            release_ids.remove(account['buddy'])
        # Don't let Niantic throttle.
        time.sleep(random.uniform(2, 4))
        response = release_pokemon(api, account, 0, release_ids)

        # Check for reCaptcha.
        captcha = account_manager.handle_captcha(
            account, status, api, response)
        if captcha['found'] and captcha['failed']:
            # Note: Account was removed from rotation.
            return False
        elif captcha['found']:
            # Make another release pokemon request.
            response = release_pokemon(api, account, 0, release_ids)

        if not response or 'RELEASE_POKEMON' not in response['responses']:
            log.error('Failed to release Pokemon.')
            return False

        release_result = response['responses']['RELEASE_POKEMON'].result

        if release_result == 1:
            log.info('Sucessfully Released %s Pokemon', len(release_ids))
            for p_id in release_ids:
                account['pokemons'].pop(p_id, None)
        else:
            log.error('Failed to release Pokemon. Unknown result %d.',
                      release_result)

    for item_id, item_name in items:
        item_count = account['items'].get(item_id, 0)
        random_max = random.randint(5, 10)
        if item_count > random_max:
            drop_count = item_count - random_max

            # Don't let Niantic throttle.
            time.sleep(random.uniform(2, 4))
            resp = recycle_inventory_item(api, account, item_id, drop_count)

            # Check for reCaptcha.
            captcha = account_manager.handle_captcha(
                account, status, api, resp)
            if captcha['found'] and captcha['failed']:
                # Note: Account was removed from rotation.
                return False
            elif captcha['found']:
                # Make another release inventory item request.
                resp = recycle_inventory_item(
                    api, account, item_id, drop_count)

            if not resp or 'RECYCLE_INVENTORY_ITEM' not in resp['responses']:
                log.error('Failed to clear inventory items.')
                return False

            clear_result = resp['responses']['RECYCLE_INVENTORY_ITEM'].result
            if clear_result == 1:
                log.info('Clearing %s %ss succeeded.', drop_count, item_name)
            elif clear_result == 2:
                log.debug('Not enough items to clear, parsing failed.')
            elif clear_result == 3:
                log.debug('Tried to recycle incubator, parsing failed.')
            else:
                log.error('Failed to clear inventory. Unknown result %d.',
                          clear_result)

    return


def incubate_eggs(api, account):
    account['eggs'] = sorted(account['eggs'], key=lambda k: k['km_target'])
    for incubator in account['incubators']:
        if not account['eggs']:
            log.debug('Account %s has no eggs to incubate.',
                      account['username'])
            break
        egg = account['eggs'].pop(0)
        time.sleep(random.uniform(2.0, 4.0))
        if use_item_egg_incubator(api, account, incubator['id'], egg['id']):
            log.info('Egg #%s (%.0f km) is on incubator #%s.',
                     egg['id'], egg['km_target'], incubator['id'])
            account['incubators'].remove(incubator)
        else:
            log.warning('Failed to put egg on incubator #%s.', incubator['id'])

    return


def parse_level_up_rewards(api, account):
    resp = level_up_rewards(api, account)
    result = resp['responses']['LEVEL_UP_REWARDS'].result
    if result == 1:
        log.info('Account %s collected its level up rewards.',
                 account['username'])
    elif result == 2:
        log.debug('Account %s already collected its level up rewards.',
                  account['username'])
    else:
        log.error('Error collecting rewards of account %s.',
                  account['username'])

#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import time
import random

log = logging.getLogger(__name__)


# This class provides requests and procedures around an api object for various
# API related functions in RocketMap.
class PGoClient:

    # Initiate a new PGoClient object with a previously freshly created api.
    def __init__(self, api):
        self.api = api
        self.timestamp = 0  # api timestamp in ms

    # Get and set methods
    # -------------------
    def get_api(self):
        return self.api

    def set_api(self, api):
        self.api = api
        self.reset_timestamp()  # New API, reset timestamp.

    def set_position(self, position):
        self.api.set_position(*position)

    def activate_hash_server(self, key):
        self.api.activate_hash_server(key)

    # Returns the new_timestamp_ms for the previous API call.
    def get_last_timestamp(self):
        return self.timestamp

    # Reset the timestamp to obtain the whole inventory on the next API call.
    # Better is a continous updating of the inventory, starting with login.
    def reset_timestamp(self):
        self.timestamp = 0

    # Requests
    # --------
    # This is an empty request, used as the very first one, after auth.
    def empty_request(self):
        request = self.api.create_request()
        return self.call(request, sequence=False)

    # General request to retrieve player information regarding locales.
    # If used during the first login, no call sequence should be made.
    def get_player(self, player_locale, login=False):
        request = self.api.create_request()
        request.get_player(player_locale=player_locale)
        return self.call(request, sequence=not login)

    # Gets player medals. Used during tutorial.
    # Called during login with additional download of settings.
    def get_player_profile(self, login=False):
        request = self.api.create_request()
        request.get_player_profile()
        return self.call(request, download_settings=login)

    # Retrieve player awards on level up.
    # Called during login with additional download of settings.
    def level_up_rewards(self, level, login=False):
        request = self.api.create_request()
        request.level_up_rewards(level=level)
        return self.call(request, download_settings=login)

    # Request for retrieving map objects from the API.
    def get_map_objects(self, latitude, longitude, since_timestamp_ms,
                        cell_id):
        request = self.api.create_request()
        request.get_map_objects(latitude=latitude,
                                longitude=longitude,
                                since_timestamp_ms=since_timestamp_ms,
                                cell_id=cell_id)
        return self.call(request)

    # Request for encountering pokemon to retrieve additional information
    def encounter(self, encounter_id, spawn_point_id,
                  player_latitude, player_longitude):
        request = self.api.create_request()
        request.encounter(encounter_id=encounter_id,
                          spawn_point_id=spawn_point_id,
                          player_latitude=player_latitude,
                          player_longitude=player_longitude)
        return self.call(request)

    # Request to spin a pokestop.
    def fort_search(self, fort_id, fort_latitude, fort_longitude,
                    player_latitude, player_longitude):
        request = self.api.create_request()
        request.fort_search(fort_id=fort_id,
                            fort_latitude=fort_latitude,
                            fort_longitude=fort_longitude,
                            player_latitude=player_latitude,
                            player_longitude=player_longitude)
        return self.call(request)

    # Functional class methods
    # ------------------------
    # Standard call method for most API requests.
    # Adjust 'sequence' or 'download_settings' argument to opt out or in.
    def call(self, request, sequence=True, download_settings=False):
        if sequence:
            request.check_challenge()
            request.get_hatched_eggs()
            request.get_inventory(last_timestamp_ms=self.timestamp)
            request.check_awarded_badges()
            if download_settings:  # Only called during login procedure
                request.download_settings()

            request.get_buddy_walked()

        response = request.call()

        self.update_timestamp(response)
        return response

    # Updates the last_timestamp_ms for get_player requests.
    def update_timestamp(self, response):
        if 'GET_INVENTORY' in response.get('responses', {}):
            self.timestamp = (response['responses']
                                      ['GET_INVENTORY']
                                      ['inventory_delta']
                              .get('new_timestamp_ms', 0))

    # Procedures
    # ----------
    # TODO: Move check_login here (for later PRs).
    # TODO: Move tutorial here (for later PRs).
    # TODO: Move runtime API procedures here (for later PRs).
    #       Here should be requested: GMO, gym details, encounter details,
    #       pokestop spins dedicated for RM including possible exceptions.

    # Login process, called during check_login if not already logged in.
    def login_procedure(self, account):
        try:  # Prevent cyclic import, we only need it here
            from .account import update_player_level
        except ImportError as e:

            log.error('Login for account %s failed. ' +
                      'Failed to import function: %s',
                      account['username'], repr(e))

        try:  # 0 - Empty request to start the procedure.
            self.empty_request()
        except Exception as e:
            log.error('Login for account %s failed. ' +
                      'Exception in initial request: %s',
                      account['username'], repr(e))

        # Possible additional config, asset and templates download, here.

        time.sleep(random.uniform(.43, .97))
        try:  # 1 - Get player data
            self.get_player(player_locale={'country': 'US',
                                           'language': 'en',
                                           'timezone': 'America/Denver'},
                            login=True)
        except Exception as e:
            log.error('Login for account %s failed. ' +
                      'Exception in getting the player data: %s',
                      account['username'], repr(e))

        time.sleep(random.uniform(.53, 1.1))
        try:  # 2 - Get player profile
            response = self.get_player_profile(login=True)
            update_player_level(account, response)  # Update account level
        except Exception as e:
            log.error('Login for account %s failed. ' +
                      'Exception in getting the player profile: %s',
                      account['username'], repr(e))

        time.sleep(random.uniform(.2, .3))
        try:  # 3 - Get level-up rewards
            response = self.level_up_rewards(level=account['level'],
                                             login=True)
            update_player_level(account, response)
        except Exception as e:
            log.error('Login for account %s failed. ' +
                      'Exception in getting the level-up rewards: %s',
                      account['username'], repr(e))

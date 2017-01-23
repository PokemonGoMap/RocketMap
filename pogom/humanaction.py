#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import time

from math import asin, atan, cos, exp, log, pi, sin, sqrt, tan

log = logging.getLogger(__name__)

def spin_pokestop(api, position, pokestops):
    pokestops_in_range = get_forts_in_range(pokestops, position)
    SPIN_REQUEST_RESULT_SUCCESS = 1
    SPIN_REQUEST_RESULT_OUT_OF_RANGE = 2
    SPIN_REQUEST_RESULT_IN_COOLDOWN_PERIOD = 3
    SPIN_REQUEST_RESULT_INVENTORY_FULL = 4
    for pokestop in pokestops_in_range:
        log.info("Trying to Drop a Pokeball")
        time.sleep(10)
        req = api.create_request()
        response_dict = req.recycle_inventory_item(item_id=1,
                        count=1
                        )
        response_dict = req.call()
        #log.info(response_dict)
        if ('responses' in response_dict) and ('RECYCLE_INVENTORY_ITEM' in response_dict['responses']):
            drop_details = response_dict['responses']['RECYCLE_INVENTORY_ITEM']
            drop_result = drop_details.get('result', -1)
            if (drop_result == 1):
                log.info("Dropped a Pokeball")
            else:
                log.info("Couldn't Drop Pokeball")            
        if pokestop.get('type') != 1:
            log.info("That was a gym")
            continue
        log.info("Found a pokestop in spin range")
        time.sleep(5)
        req = api.create_request()
        response_dict = req.fort_search(fort_id=pokestop['id'],
                        fort_latitude=pokestop['latitude'],
                        fort_longitude=pokestop['longitude'],
                        player_latitude=pokestop['latitude'],
                        player_longitude=pokestop['longitude']
                        )   
        response_dict = req.call()
        #log.info(response_dict)
        if ('responses' in response_dict) and ('FORT_SEARCH' in response_dict['responses']):
                spin_details = response_dict['responses']['FORT_SEARCH']
                spin_result = spin_details.get('result', -1)
                if (spin_result == SPIN_REQUEST_RESULT_SUCCESS) or (spin_result == SPIN_REQUEST_RESULT_INVENTORY_FULL):
                    experience_awarded = spin_details.get('experience_awarded', 0)
                    if experience_awarded:
                        log.info("Spun pokestop got response data!")
                    else:
                        log.info('Found nothing in pokestop') 
                elif spin_result == SPIN_REQUEST_RESULT_OUT_OF_RANGE:
                    log.info("Pokestop out of range.")
                elif spin_result == SPIN_REQUEST_RESULT_IN_COOLDOWN_PERIOD:
                    log.info("Pokestop in cooldown")
                else:
                    log.info("unknown pokestop return")              
    return  


def get_forts_in_range(pokestops, scan_location):
    log.info("Checking for pokestops in spin range")
    MAX_DISTANCE_FORT_IS_REACHABLE = 38 # meters
    MAX_DISTANCE_POKEMON_IS_REACHABLE = 48
    forts = pokestops
    forts = filter(lambda fort: fort["id"], forts)
    forts = filter(lambda fort: distance(
        scan_location[0],
        scan_location[1],
        fort['latitude'],
        fort['longitude']
    ) <= MAX_DISTANCE_FORT_IS_REACHABLE, forts)

    return forts    

def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * \
        cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a)) * 1000
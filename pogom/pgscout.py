import logging
import sys

import requests

from pogom.utils import get_args

log = logging.getLogger(__name__)


def scout_error(error_msg):
    log.error(error_msg)
    return {
        "success": False,
        "error": error_msg
    }


def pgscout_encounter(p):
    args = get_args()

    # Assemble PGScout request
    params = {
        'pokemon_id': p.pokemon_id,
        'encounter_id': p.encounter_id,
        'spawn_point_id': p.spawnpoint_id,
        'latitude': p.latitude,
        'longitude': p.longitude
    }
    try:
        r = requests.get(args.pgscout_url, params=params)
    except:
        return scout_error(
            "Exception on scout: {}".format(repr(sys.exc_info()[1])))

    return r.json() if r.status_code == 200 else scout_error(
        "Got error {} from scout service.".format(r.status_code))

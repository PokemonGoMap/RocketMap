#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from matplotlib.path import Path
from ast import literal_eval

log = logging.getLogger(__name__)


# Create geofence. This is very, very WIP!

def geofence(results, geofence_file, forbidden=False):
    geofence = []
    with open(geofence_file) as f:
        for line in f:
            if len(line.strip()) == 0 or line.startswith('#'):
                continue
            geofence.append(literal_eval(line.strip()))
        if forbidden:
            log.info('Loaded %d geofence-forbidden coordinates. ' +
                     'Applying...', len(geofence))
        else:
            log.info('Loaded %d geofence coordinates. Applying...',
                     len(geofence))
    log.info(geofence)
    p = Path(geofence)
    results_geofenced = []
    for g in range(len(results)):
        result_x, result_y, result_z = results[g]
        if p.contains_point([result_x, result_y]) ^ forbidden:
            results_geofenced.append((result_x, result_y, result_z))
    return results_geofenced

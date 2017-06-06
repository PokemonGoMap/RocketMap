#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import logging

from .utils import get_args

log = logging.getLogger(__name__)

args = get_args()

# Trying to import matplotlib, which is not compatible with all hardware.
# Matlplotlib is faster for big calculations.
try:
    from matplotlib.path import Path
except ImportError as e:
    if not args.no_matplotlib:
        log.error('Exception while importing "matplotlib": %s', repr(e))
        log.error(
            'Aborting. Install "matplotlib" or ' +
            'enable "-nmptl" or "--no-matplotlib" to circumvent.')
        sys.exit()
    else:
        pass


class Geofences:

    def __init__(self):
        self.valid_areas = []
        self.forbidden_areas = []

        if args.geofence_file or args.forbidden_file:
            log.info('Looking for geofenced or forbidden areas.')
            self.valid_areas = self.parse_geofences_file(
                args.geofence_file, forbidden=False)
            self.forbidden_areas = self.parse_geofences_file(
                args.forbidden_file, forbidden=True)
            log.info(
                'Loaded %d valid and %d forbidden areas',
                len(self.valid_areas),
                len(self.forbidden_areas))

    def is_enabled(self):
        enabled = False
        if self.valid_areas or self.forbidden_areas:
            enabled = True

        return enabled

    def get_geofenced_coordinates(self, coordinates):
        log.info('Found %d coordinates to geofence.', len(coordinates))
        geofenced_coordinates = []
        startTime = time.time()
        if self.valid_areas:
            for c in coordinates:
                for va in self.valid_areas:
                    if self.is_coordinate_in_geofence(c, va):
                        # Coordinate is valid if in one valid area.
                        geofenced_coordinates.append(c)
                        break
        else:
            geofenced_coordinates = coordinates

        if self.forbidden_areas:
            for c in reversed(geofenced_coordinates):
                for fa in self.forbidden_areas:
                    if self.is_coordinate_in_geofence(c, fa):
                        # Coordinate is invalid if in one forbidden area.
                        geofenced_coordinates.pop(
                            geofenced_coordinates.index(c))
                        break

        endTime = time.time()
        elapsedTime = endTime - startTime
        log.info(
            'Geofenced to %s coordinates in %.2f s.',
            len(geofenced_coordinates), elapsedTime)

        return geofenced_coordinates

    def is_coordinate_in_geofence(self, coordinate, geofence):
        if args.spawnpoint_scanning:
            point = {'lat': coordinate['lat'], 'lon': coordinate['lng']}
        else:
            point = {'lat': coordinate[0], 'lon': coordinate[1]}
        polygon = geofence['polygon']
        if args.no_matplotlib:
            return self.is_point_in_polygon_custom(point, polygon)
        else:
            return self.is_point_in_polygon_matplotlib(point, polygon)

    @staticmethod
    def parse_geofences_file(geofence_file, forbidden):
        geofences = []
        # Read coordinates of forbidden areas from file.
        if geofence_file:
            with open(geofence_file) as f:
                for line in f:
                    if len(line.strip()) == 0:  # Empty line.
                        continue
                    elif line.startswith("["):  # Name line.
                        name = line.strip().replace("[", "").replace("]", "")
                        geofences.append({
                            'forbidden': forbidden,
                            'name': name,
                            'polygon': []
                        })
                        log.debug('Found geofence: %s', name)
                    else:  # Coordinate line.
                        lat, lon = line.strip().split(",")
                        LatLon = {'lat': float(lat), 'lon': float(lon)}
                        geofences[-1]['polygon'].append(LatLon)

        return geofences

    @staticmethod
    def is_point_in_polygon_matplotlib(point, polygon):
        pointTouple = (point['lat'], point['lon'])
        polygonToupleList = []
        for c in polygon:
            coordinateTouple = (c['lat'], c['lon'])
            polygonToupleList.append(coordinateTouple)

        polygonToupleList.append(polygonToupleList[0])
        path = Path(polygonToupleList)

        return path.contains_point(pointTouple)

    @staticmethod
    def is_point_in_polygon_custom(point, polygon):
        # Initialize first coordinate as default.
        maxLat = polygon[0]['lat']
        minLat = polygon[0]['lat']
        maxLon = polygon[0]['lon']
        minLon = polygon[0]['lon']

        for coords in polygon:
            maxLat = max(coords['lat'], maxLat)
            minLat = min(coords['lat'], minLat)
            maxLon = max(coords['lon'], maxLon)
            minLon = min(coords['lon'], minLon)

        if ((point['lat'] > maxLat) or (point['lat'] < minLat) or
                (point['lon'] > maxLon) or (point['lon'] < minLon)):
            return False

        inside = False
        lat1, lon1 = polygon[0]['lat'], polygon[0]['lon']
        N = len(polygon)
        for n in range(1, N+1):
            lat2, lon2 = polygon[n % N]['lat'], polygon[n % N]['lon']
            if (min(lon1, lon2) < point['lon'] <= max(lon1, lon2) and
                    point['lat'] <= max(lat1, lat2)):
                        if lon1 != lon2:
                            latIntersection = (
                                (point['lon'] - lon1) *
                                (lat2 - lat1) / (lon2 - lon1) +
                                lat1)

                        if lat1 == lat2 or point['lat'] <= latIntersection:
                            inside = not inside

            lat1, lon1 = lat2, lon2

        return inside

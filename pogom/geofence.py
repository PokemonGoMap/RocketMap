#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import logging

from .models import Geofence

log = logging.getLogger(__name__)

try:
    from matplotlib.path import Path
except ImportError as e:
    log.warning('Exception while importing matplotlib: %s', repr(e))
    log.warning('Enable "-nmptl" or "--no-matplotlib" to circumvent.')
    pass


class Geofences:
    def __init__(self, args, db_updates_queue):
        self.args = args
        self.geofences = {}
        self.valid_areas = []
        self.forbidden_areas = []
        self.db_updates_queue = db_updates_queue

        if args.purge_geofence_data:  # Remove old geofences from DB.
            Geofence.clear_all()

        # Initialization of object when geofence files are provided.
        if self.args.geofence_file or self.args.forbidden_file:
            self.geofence_file = self.args.geofence_file
            self.forbidden_file = self.args.forbidden_file

            self.parse_geofences()
            self.push_db_geofences()

    def get_geofences(self):
        return self.geofences

    def is_enabled(self):
        enabled = False
        if self.geofences:
            enabled = True

        return enabled

    def parse_geofences(self):
        geofence_data = {}
        lenGeofenceData = 0
        name = ''
        log.info('Looking for geofenced or forbidden areas.')

        i = 0
        if self.geofence_file:
            j = 0
            startTime = time.time()

            # Read coordinates of geofences from file.
            with open(self.geofence_file) as f:
                for line in f:
                    if len(line.strip()) == 0:
                        continue
                    elif line.startswith("["):
                        i = i + 1
                        nameLine = line.strip()
                        nameLine = nameLine.replace("[", "")
                        name = nameLine.replace("]", "")
                        log.debug('Found geofence: %s', name)
                        continue

                    if i not in geofence_data:
                        j = j + 1
                        geofence_data[i] = {}
                        geofence_data[i]['forbidden'] = False
                        geofence_data[i]['name'] = name
                        geofence_data[i]['polygon'] = []
                        lat, lon = line.strip().split(",")
                        LatLon = {'lat': float(lat), 'lon': float(lon)}
                        geofence_data[i]['polygon'].append(LatLon)
                    else:
                        j = j + 1
                        lat, lon = (line.strip()).split(",")
                        LatLon = {'lat': float(lat), 'lon': float(lon)}
                        geofence_data[i]['polygon'].append(LatLon)

            endTime = time.time()
            elapsedTime = endTime - startTime
            lenGeofenceData = len(geofence_data)
            log.info(
                'Loaded %d geofences with a total of %d coordinates ' +
                'in %.2f s.',
                lenGeofenceData, j, elapsedTime)

        if self.forbidden_file:
            j = 0
            startTime = time.time()

            # Read coordinates of forbidden areas from file.
            with open(self.forbidden_file) as f:
                for line in f:
                    if len(line.strip()) == 0:
                        continue
                    elif line.startswith("["):
                        i = i + 1
                        nameLine = line.strip()
                        nameLine = nameLine.replace("[", "")
                        name = nameLine.replace("]", "")
                        log.debug('Found forbidden area: %s', name)
                        continue

                    if i not in geofence_data:
                        j = j + 1
                        geofence_data[i] = {}
                        geofence_data[i]['forbidden'] = True
                        geofence_data[i]['name'] = name
                        geofence_data[i]['polygon'] = []
                        lat, lon = line.strip().split(",")
                        LatLon = {'lat': float(lat), 'lon': float(lon)}
                        geofence_data[i]['polygon'].append(LatLon)
                    else:
                        j = j + 1
                        lat, lon = (line.strip()).split(",")
                        LatLon = {'lat': float(lat), 'lon': float(lon)}
                        geofence_data[i]['polygon'].append(LatLon)

            endTime = time.time()
            elapsedTime = endTime - startTime
            log.info(
                'Loaded %d forbidden areas with a total of %d coordinates ' +
                'in %.2f s.',
                len(geofence_data) - lenGeofenceData, j, elapsedTime)

        self.geofences = geofence_data

        for g in self.geofences:
            if self.geofences[g]['forbidden']:
                self.forbidden_areas.append(self.geofences[g])
            else:
                self.valid_areas.append(self.geofences[g])

    def get_geofenced_coordinates(self, coordinates):
        log.info('Found %d coordinates to geofence.', len(coordinates))
        geofenced_coordinates = []
        startTime = time.time()
        if self.valid_areas:
            for c in coordinates:
                if self.args.spawnpoint_scanning:
                    point = {'lat': c['lat'], 'lon': c['lng']}
                else:
                    point = {'lat': c[0], 'lon': c[1]}
                for va in self.valid_areas:
                    if self.args.no_matplotlib:
                        if self.point_in_polygon_custom(
                                point, va['polygon']):
                            # Coordinate is valid if in one valid area.
                            geofenced_coordinates.append(c)
                            break
                    else:
                        if self.point_in_polygon_matplotlib(
                                point, va['polygon']):
                            # Coordinate is valid if in one valid area.
                            geofenced_coordinates.append(c)
                            break
        else:
            geofenced_coordinates = coordinates

        if self.forbidden_areas:
            for c in reversed(geofenced_coordinates):
                if self.args.spawnpoint_scanning:
                    point = {'lat': c['lat'], 'lon': c['lng']}
                else:
                    point = {'lat': c[0], 'lon': c[1]}
                for fa in self.forbidden_areas:
                    if self.args.no_matplotlib:
                        if self.point_in_polygon_custom(
                                point, fa['polygon']):
                            # Coordinate is invalid if in one forbidden area.
                            geofenced_coordinates.pop(
                                geofenced_coordinates.index(c))
                            break
                    else:
                        if self.point_in_polygon_matplotlib(
                                point, fa['polygon']):
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

    def push_db_geofences(self):
        db_geofences = {}
        key = 0
        id = 0
        for key in range(1, len(self.geofences) + 1):
            coords = 0
            for coords in range(0, len(self.geofences[key]['polygon'])):
                id = id + 1
                db_geofences[id] = {
                    'geofence_id': key,
                    'forbidden': self.geofences[key]['forbidden'],
                    'name': self.geofences[key]['name'],
                    'coordinates_id': coords,
                    'latitude': self.geofences[key]['polygon'][coords]['lat'],
                    'longitude': self.geofences[key]['polygon'][coords]['lon']
                }

        self.db_updates_queue.put((Geofence, db_geofences))
        log.debug('Upserted %d geofence entries.', len(db_geofences))

    @staticmethod
    def point_in_polygon_matplotlib(point, polygon):
        pointTouple = (point['lat'], point['lon'])
        polygonToupleList = []
        for c in polygon:
            coordinateTouple = (c['lat'], c['lon'])
            polygonToupleList.append(coordinateTouple)

        polygonToupleList.append(polygonToupleList[0])
        path = Path(polygonToupleList)

        return path.contains_point(pointTouple)

    @staticmethod
    def point_in_polygon_custom(point, polygon):
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

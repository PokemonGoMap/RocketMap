#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import logging

from .models import Geofence

log = logging.getLogger(__name__)


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
            self.upsert_geofences()

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

        geofence_id = 0
        if self.geofence_file:
            coordinates_id = 0
            startTime = time.time()

            # Read coordinates of geofences from file.
            with open(self.geofence_file) as f:
                for line in f:
                    if len(line.strip()) == 0:
                        continue
                    elif line.startswith("["):
                        geofence_id = geofence_id + 1
                        nameLine = line.strip()
                        nameLine = nameLine.replace("[", "")
                        name = nameLine.replace("]", "")
                        log.debug('Found geofence: %s', name)
                        continue

                    if geofence_id not in geofence_data:
                        coordinates_id = coordinates_id + 1
                        geofence_data[geofence_id] = {}
                        geofence_data[geofence_id]['forbidden'] = False
                        geofence_data[geofence_id]['name'] = name
                        geofence_data[geofence_id]['polygon'] = []
                        lat, lon = line.strip().split(",")
                        LatLon = {'lat': float(lat), 'lon': float(lon)}
                        geofence_data[geofence_id]['polygon'].append(LatLon)
                    else:
                        coordinates_id = coordinates_id + 1
                        lat, lon = (line.strip()).split(",")
                        LatLon = {'lat': float(lat), 'lon': float(lon)}
                        geofence_data[geofence_id]['polygon'].append(LatLon)

            endTime = time.time()
            elapsedTime = endTime - startTime
            lenGeofenceData = len(geofence_data)
            log.info(
                'Loaded %d geofences with a total of %d coordinates ' +
                'in %.2f s.',
                lenGeofenceData,
                coordinates_id,
                elapsedTime)

        if self.forbidden_file:
            coordinates_id = 0
            startTime = time.time()

            # Read coordinates of forbidden areas from file.
            with open(self.forbidden_file) as f:
                for line in f:
                    if len(line.strip()) == 0:
                        continue
                    elif line.startswith("["):
                        geofence_id = geofence_id + 1
                        nameLine = line.strip()
                        nameLine = nameLine.replace("[", "")
                        name = nameLine.replace("]", "")
                        log.debug('Found forbidden area: %s', name)
                        continue

                    if geofence_id not in geofence_data:
                        coordinates_id = coordinates_id + 1
                        geofence_data[geofence_id] = {}
                        geofence_data[geofence_id]['forbidden'] = True
                        geofence_data[geofence_id]['name'] = name
                        geofence_data[geofence_id]['polygon'] = []
                        lat, lon = line.strip().split(",")
                        LatLon = {'lat': float(lat), 'lon': float(lon)}
                        geofence_data[geofence_id]['polygon'].append(LatLon)
                    else:
                        coordinates_id = coordinates_id + 1
                        lat, lon = (line.strip()).split(",")
                        LatLon = {'lat': float(lat), 'lon': float(lon)}
                        geofence_data[geofence_id]['polygon'].append(LatLon)

            endTime = time.time()
            elapsedTime = endTime - startTime
            log.info(
                'Loaded %d forbidden areas with a total of %d coordinates ' +
                'in %.2f s.',
                len(geofence_data) - lenGeofenceData,
                coordinates_id,
                elapsedTime)

        self.geofences = geofence_data

        for g in self.geofences:
            if self.geofences[g]['forbidden']:
                self.forbidden_areas.append(self.geofences[g])
            else:
                self.valid_areas.append(self.geofences[g])

    def upsert_geofences(self):
        Geofence.remove_duplicates(self.geofences)
        db_geofences = Geofence.get_db_entries(self.geofences)
        self.db_updates_queue.put((Geofence, db_geofences))
        log.debug('Upserted %d geofence entries.', len(db_geofences))

    def get_geofenced_coordinates(self, coordinates):
        log.info('Found %d coordinates to geofence.', len(coordinates))
        geofenced_coordinates = []
        startTime = time.time()
        if self.valid_areas:
            for c in coordinates:
                for va in self.valid_areas:
                    if self.is_coordinate_in_geofence(
                            c, va):
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
        if self.args.spawnpoint_scanning:
            point = {'lat': coordinate['lat'], 'lon': coordinate['lng']}
        else:
            point = {'lat': coordinate[0], 'lon': coordinate[1]}
        polygon = geofence['polygon']
        if self.args.no_matplotlib:
            return Geofence.point_in_polygon_custom(point, polygon)
        else:
            return Geofence.point_in_polygon_matplotlib(point, polygon)

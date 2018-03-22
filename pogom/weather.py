import logging

import s2sphere

from pogom.models import Weather

log = logging.getLogger(__name__)


def get_weather_cells(swLat, swLng, neLat, neLng):
    return prepare_weather_cells_data(Weather.get_weather_by_location(
        swLat, swLng, neLat, neLng, False)
    )


def get_weather_alerts(swLat, swLng, neLat, neLng):
    return prepare_weather_cells_data(Weather.get_weather_by_location(
        swLat, swLng, neLat, neLng, True)
    )


def prepare_weather_cells_data(db_weathers):
    for i in range(0, len(db_weathers)):
        cell = get_cell_from_string(db_weathers[i]['s2_cell_id'])
        center = s2sphere.LatLng.from_point(cell.get_center())
        db_weathers[i]['center'] = {
            'lat': center.lat().degrees,
            'lng': center.lng().degrees
        }
        db_weathers[i]['vertices'] = get_vertices_from_s2cell(cell)
        db_weathers[i]['s2_cell_id'] = str(cell.id().id())

    return db_weathers


# Workaround due a bug in POGOprotos.
def get_cell_from_string(str_id):
    raw_id = long(str_id)
    if raw_id < 0:  # overflow
        cell_id = s2sphere.CellId(raw_id)
        return s2sphere.Cell.from_face_pos_level(
            cell_id.face(), cell_id.pos(), 10
        )
    else:
        return s2sphere.Cell(s2sphere.CellId(raw_id))


def get_s2_coverage(swLat, swLng, neLat, neLng):
    geoms = []

    r = s2sphere.RegionCoverer()
    r.min_level = 10
    r.max_level = 10
    r.max_cells = 40
    p1 = s2sphere.LatLng.from_degrees(float(swLat), float(swLng))
    p2 = s2sphere.LatLng.from_degrees(float(neLat), float(neLng))
    covering = r.get_covering(s2sphere.LatLngRect.from_point_pair(p1, p2))

    for cell_id in covering:
        cell_to_render = {}
        rect_bound = s2sphere.Cell(cell_id)
        center = s2sphere.LatLng.from_point(rect_bound.get_center())
        cell_to_render['s2_cell_id'] = str(cell_id.id())
        cell_to_render['center'] = {
            'lat': center.lat().degrees,
            'lng': center.lng().degrees
        }
        cell_to_render['vertices'] = get_vertices_from_s2cell(rect_bound)

        del rect_bound
        geoms.append(cell_to_render)

    return geoms


# Convert s2cell vertices to Google Maps API format.
def get_vertices_from_s2cell(rect_bound):
    vertices = []
    for i in range(0, 4):
        vertex = s2sphere.LatLng.from_point(rect_bound.get_vertex(i))
        vertices.append({
            'lat': vertex.lat().degrees,
            'lng': vertex.lng().degrees
        })
    return vertices

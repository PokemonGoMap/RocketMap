#!/usr/bin/python

from pymysql import connect, cursors
from time import time
from re import sub
import os
import sys
import csv
import numpy
import configargparse

configpath = os.path.join(os.path.dirname(__file__), '../../config/config.ini')
parser = configargparse.ArgParser(default_config_files=[configpath])
parser.add_argument("--lat", help="Latitude of center", type=float, required=True)
parser.add_argument("--lng", help="Longitude of center", type=float, required=True)
parser.add_argument("-st", "--step-limit", help="Steps", default=3, type=int)
parser.add_argument("--slices", help="Heatmap slices per spawn; higher values are VERY slow", default=40, type=int)
parser.add_argument("--no-init", help="Skip database initialization; must manually populate spawnpoints table", action='store_true', default=False)
parser.add_argument('--db-name', help='Name of the database to be used')
parser.add_argument('--db-user', help='Username for the database')
parser.add_argument('--db-pass', help='Password for the database')
parser.add_argument('--db-host', help='IP or hostname for the database')
parser.add_argument('--db-port', help='Port for the database', type=int, default=3306)
parser.set_defaults(DEBUG=False)
args, unknown = parser.parse_known_args()

lat = args.lat
lng = args.lng
splat = 70
radius = args.step_limit * splat * 2
slices = args.slices
init_tables = not args.no_init
db_host = args.db_host
db_port = args.db_port
db_user = args.db_user
db_pass = args.db_pass
db_name = args.db_name
filename = 'spawns_{:.6f}_{:.6f}_{:d}m_{:d}s.csv'.format(lat, lng, radius, slices)

start_time = time()

db = connect(host = db_host, port = db_port, user = db_user, password = db_pass, db = db_name)
cur = db.cursor(cursors.DictCursor)

if init_tables:
    print('Generating spawnpoint data for {:.6g},{:.6g} ({:d}m radius using {:d} heatmap slices)'.format(lat, lng, radius, slices))
    # requires haversine() implementation in mysql; unable to do so easily with sqlite without it being horrendously ugly
    #stm = 'create function haversine(lat1 double, lng1 double, lat2 double, lng2 double) returns double deterministic return 12756274 * asin(sqrt(0.5 - cos((lat2 - lat1) * 0.017453292519943295) / 2 + cos(lat1 * 0.017453292519943295) * cos(lat2 * 0.017453292519943295) * (1 - cos((lng2 - lng1) * 0.017453292519943295)) / 2))'
    #cur.execute(stm)
    stm = 'drop table if exists spawnpoints'
    cur.execute(stm)
    stm = 'create table spawnpoints as select spawnpoint_id, avg(latitude) as lat, avg(longitude) as lng from pokemon where haversine(%f, %f, latitude, longitude) < %d group by spawnpoint_id order by spawnpoint_id asc'
    cur.execute(stm % (lat, lng, radius))

stm = 'select count(*) as pts from spawnpoints'
cur.execute(stm)
res = cur.fetchone()
spawn_total = res['pts']
spawn_count = spawn_total
print('Spawnpoints to optimize: {:d}'.format(spawn_total))

output = []
phase = 1

while spawn_count > 0:
    heatmap = {}

    # grab points favoring high-density before just grabbing whatever is left
    if phase == 1:
        stm = 'select s1.spawnpoint_id, s1.lat, s1.lng from spawnpoints s1 cross join spawnpoints s2 on (s1.spawnpoint_id != s2.spawnpoint_id and haversine(s1.lat, s1.lng, s2.lat, s2.lng) < %f * 2) group by s1.spawnpoint_id, s1.lat, s1.lng order by count(*) desc limit 1'
        cur.execute(stm % splat)
        if cur.rowcount == 0:
            print('\r\033[KEvaluating unconnected points')
            phase += 1
            continue
    else:
        stm = 'select spawnpoint_id, lat, lng from spawnpoints limit 1'
        cur.execute(stm)
    res = cur.fetchone()
    point = {'spawnpoint_id': res['spawnpoint_id'], 'lat': res['lat'], 'lng': res['lng']}

    bar = '=' * int(round(30 * (spawn_total - spawn_count) / spawn_total))
    bar = sub('=$', '>', bar)
    sys.stdout.write("\r\033[K[{:30s}] Determining local maxima near {:.8g},{:.8g}".format(bar, point['lat'], point['lng']))
    sys.stdout.flush()

    for i in numpy.linspace(point['lat'] - 0.001, point['lat'], slices):
        for j in numpy.linspace(point['lng'] - 0.001, point['lng'] + 0.001, slices):
            stm = 'select count(*) as pts from spawnpoints where haversine(%f, %f, lat, lng) < %f'
            cur.execute(stm % (i, j, splat))
            res = cur.fetchone()
            nearby = res['pts']

            if nearby > 0:
                heatmap['{:.23g},{:.23g}'.format(i, j)] = nearby

    heatmap_sorted = sorted(heatmap, key=lambda x: heatmap[x])
    sorted_coord = heatmap_sorted[-1]
    sorted_val = heatmap[sorted_coord]

    # only use local peak if heatmap height isnt 1
    if sorted_val != 1:
        coord = sorted_coord.split(',')
        point['lat'] = float(coord[0])
        point['lng'] = float(coord[1])
        point['spawnpoint_id'] = '{}_peak'.format(point['spawnpoint_id'])

    output.append(point)

    # clear points that this scan would cover
    stm = 'delete from spawnpoints where haversine(%f, %f, lat, lng) < %f'
    cur.execute(stm % (point['lat'], point['lng'], splat))

    # how many spawnpoints are now left
    stm = 'select count(*) as pts from spawnpoints'
    cur.execute(stm)
    res = cur.fetchone()
    spawn_count = res['pts']

print('\r\033[K[{}] Heatmap generation complete\nFull coverage required {:d} scan locations'.format('=' * 30, len(output)))

print('Cleaning up database')
stm = 'truncate table spawnpoints'
cur.execute(stm)

with open(filename, 'w') as csvfile:
    cols = ['spawnpoint_id', 'lat', 'lng']
    out = csv.DictWriter(csvfile, fieldnames=cols)

    out.writeheader()
    map(out.writerow, output)

diff = time() - start_time
print('Coverage approximation via heatmap took {:.4f} seconds'.format(diff))
print('Optimized scan coordinates saved to {}'.format(filename))


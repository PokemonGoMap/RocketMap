import os
import sys
import configargparse

import logging
import json
from math import ceil

from operator import itemgetter

logging.basicConfig(format='%(asctime)s [%(threadName)16s][%(module)14s][%(levelname)8s] %(message)s')
log = logging.getLogger(__name__)

def split_spawns(spawns, filename, accounts, sort, path, index, nw_lat, nw_lng, se_lat, se_lng):
    spawns.sort(key=itemgetter(sort))
    
    split_spawns = []
    for i in range(0, accounts):
        split_spawns.append([])
    
    spawn_count = len(spawns)
    spawn_count_each = int(spawn_count / accounts)
    
    log.info("splitting %d spawns to %d accounts: %d each, meaning max %ds per scan" % (spawn_count, accounts, spawn_count_each, ceil(3600/spawn_count_each)))
    
    spawn_count = 0
    account_count = 0
    for item in spawns:
        newitem = {}
        newitem["lat"] = float(item["lat"])
        newitem["lng"] = float(item["lng"])
        newitem["time"] = int(float(item["time"]))
        if((nw_lat and se_lat) and (nw_lat < newitem["lat"] or se_lat > newitem["lat"])):
            continue
        if((nw_lng and se_lng) and (nw_lng > newitem["lng"] or se_lng < newitem["lng"])):
            continue
        split_spawns[spawn_count % accounts].append(newitem)
        spawn_count = spawn_count + 1
    
    spawn_count_each = int(spawn_count / accounts)
    log.info("splitted %d spawns to %d accounts: %d each, meaning max %ds per scan" % (spawn_count, accounts, spawn_count_each, ceil(3600/spawn_count_each)))
    filename = filename.replace(".json", "")
    
    if not os.path.exists(path):
        os.makedirs(path)
    
    for i in range(0, accounts):
        data = split_spawns[i]
        with open("%s/%s_%d.json" % (path, filename, i + index), 'w') as outfile:
            json.dump(data, outfile)
    
   
def get_args():
    # fuck PEP8
    parser = configargparse.ArgParser()
    parser.add_argument('-a', '--accounts',
                        type=int,
                        help='Account Number',
                        required=True)
    parser.add_argument('-f', '--filename',
                        help='filename of spawn json',
                        required=True)
    parser.add_argument('-s', '--sort',
                        help='Sorting: lat or lng',
                        required=True)
    parser.add_argument('-p', '--path',
                        help='output path',
                        default='.')
    parser.add_argument('-i', '--index',
                        type=int,
                        help='start index of output files',
                        default=0)
    parser.add_argument('-nwlt', '--north-west-lat',
                        type=float)
    parser.add_argument('-nwlg', '--north-west-lng',
                        type=float)
    parser.add_argument('-selt', '--south-east-lat',
                        type=float)
    parser.add_argument('-selg', '--south-east-lng',
                        type=float)
    parser.set_defaults(DEBUG=False)

    args = parser.parse_args()
    
    if not ((args.north_west_lat and args.north_west_lng and args.south_east_lat and args.south_east_lng) or
        (args.north_west_lat is None and args.north_west_lng is None and args.south_east_lat is None and args.south_east_lng is None)):
        parser.print_usage()
        print(sys.argv[0] + ": error: you need both north-west and south-east or none")
        sys.exit(1)
    
    if(args.sort  != "lat" and args.sort  != "lng"):
        parser.print_usage()
        print(sys.argv[0] + ": error: arguments -s/--sort is required")
        sys.exit(1)
    
    return args

if __name__ == '__main__':
    log.setLevel(logging.INFO)
    args = get_args()
    
    try:
        with open(args.filename) as file:
            try:
                spawns = json.load(file)
                
                try:
                    split_spawns(spawns, args.filename, args.accounts, args.sort, args.path, args.index, args.north_west_lat, args.north_west_lng, args.south_east_lat, args.south_east_lng)
                except Exception as e:
                    log.error("Error while executing split_spawns(): " + str(e))
            except ValueError as e:
                log.error(args.filename + " is not valid: " + str(e))
                sys.exit(1)
            
            file.close()
    except IOError:
        log.error("Error opening " + args.filename)
        sys.exit(1)
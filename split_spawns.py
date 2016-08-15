import os
import sys
import configargparse

import logging
import json
from math import ceil

from operator import itemgetter

logging.basicConfig(format='%(asctime)s [%(threadName)16s][%(module)14s][%(levelname)8s] %(message)s')
log = logging.getLogger(__name__)

def split_spawns(spawns, filename, accounts, sort, path, index):
    spawns.sort(key=itemgetter(sort))
    
    split_spawns = []
    for i in range(0, accounts):
        split_spawns.append([])
    
    spawn_count = len(spawns)
    spawn_count_each = int(spawn_count / accounts)
    
    log.info("splitting %d spawns to %d accounts: %d each, meaning max %ds per scan" % (spawn_count, accounts, spawn_count_each, ceil(3600/spawn_count_each)))
    
    i = 0
    account_count = 0
    for item in spawns:
        split_spawns[account_count].append(item)
        i = i + 1
        if i > spawn_count_each:
            account_count = account_count + 1
            i = 0
    
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
    parser.set_defaults(DEBUG=False)

    args = parser.parse_args()
    
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
                    split_spawns(spawns, args.filename, args.accounts, args.sort, args.path, args.index)
                except Exception as e:
                    log.error("Error while executing split_spawns(): " + str(e))
            except ValueError as e:
                log.error(args.filename + " is not valid: " + str(e))
                sys.exit(1)
            
            file.close()
    except IOError:
        log.error("Error opening " + args.filename)
        sys.exit(1)
from pogom.utils import get_args
from datetime import datetime

args = get_args()
# Temporarily disabling because -o and -i is removed from 51f651228c00a96b86f5c38d1a2d53b32e5d9862.
# IGNORE = None
# ONLY = None
# if args.ignore:
#     IGNORE =  [i.lower().strip() for i in args.ignore.split(',')]
# elif args.only:
#     ONLY = [i.lower().strip() for i in args.only.split(',')]


def printPokemon(pokemon, lat, lng, itime):
    pokemon_name = pokemon['name']
    pokemon_rarity = pokemon['rarity']
    pokemon_id = str(pokemon['id'])
    time_left = itime - datetime.utcnow()
    print("======================================\n"
          " Name: %s\n Rarity: %s\n Coord: (%f,%f)\n"
          " ID: %s \n"
          " Remaining Time: %s\n"
          "======================================" %
          (pokemon_name.encode('utf-8'), pokemon_rarity.encode('utf-8'), lat, lng, pokemon_id, str(time_left)))

#!/usr/bin/env python
from __future__ import division

# -*- coding: utf-8 -*-
#
# Simple Bot to send timed Telegram messages
# This program is dedicated to the public domain under the CC0 license.
    
import logging
from telegram.ext import Updater, StringCommandHandler, StringRegexHandler, MessageHandler, CommandHandler, RegexHandler, Filters, Job
from telegram.ext.dispatcher import run_async
from telegram import Location
from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut, NetworkError
import telegram
import ConfigParser
import math

from datetime import datetime, timedelta
from dateutil import tz
from pytz import timezone
from copy import deepcopy
from pymongo import MongoClient

from pygeocoder import Geocoder
from pygeolib import GeocoderError
import coloredlogs
import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

botconfig = ConfigParser.RawConfigParser()
botconfig.read('config/bot.ini')


    
TOKEN = botconfig.get('telegram', 'token')
URI = botconfig.get('pymongo', 'uri')

varpath = 'var/'
client = MongoClient(URI)
db = client.pogom
users = db.users
gc_counts = db.gc_counts


bot = telegram.bot.Bot(TOKEN)
log = logging.getLogger(__name__)
time_db_check = datetime.utcnow()
_maxGC = 400
_max_ping_distance=1500
_max_message_distance=5000
   
pokemonDict = {
    1: "Bulbasaur",
    2: "Ivysaur",
    3: "Venusaur",
    4: "Charmander",
    5: "Charmeleon",
    6: "Charizard",
    7: "Squirtle",
    8: "Wartortle",
    9: "Blastoise",
    10: "Caterpie",
    11: "Metapod",
    12: "Butterfree",
    13: "Weedle",
    14: "Kakuna",
    15: "Beedrill",
    16: "Pidgey",
    17: "Pidgeotto",
    18: "Pidgeot",
    19: "Rattata",
    20: "Raticate",
    21: "Spearow",
    22: "Fearow",
    23: "Ekans",
    24: "Arbok",
    25: "Pikachu",
    26: "Raichu",
    27: "Sandshrew",
    28: "Sandslash",
    29: "Nidoran?",
    30: "Nidorina",
    31: "Nidoqueen",
    32: "Nidoran?",
    33: "Nidorino",
    34: "Nidoking",
    35: "Clefairy",
    36: "Clefable",
    37: "Vulpix",
    38: "Ninetales",
    39: "Jigglypuff",
    40: "Wigglytuff",
    41: "Zubat",
    42: "Golbat",
    43: "Oddish",
    44: "Gloom",
    45: "Vileplume",
    46: "Paras",
    47: "Parasect",
    48: "Venonat",
    49: "Venomoth",
    50: "Diglett",
    51: "Dugtrio",
    52: "Meowth",
    53: "Persian",
    54: "Psyduck",
    55: "Golduck",
    56: "Mankey",
    57: "Primeape",
    58: "Growlithe",
    59: "Arcanine",
    60: "Poliwag",
    61: "Poliwhirl",
    62: "Poliwrath",
    63: "Abra",
    64: "Kadabra",
    65: "Alakazam",
    66: "Machop",
    67: "Machoke",
    68: "Machamp",
    69: "Bellsprout",
    70: "Weepinbell",
    71: "Victreebel",
    72: "Tentacool",
    73: "Tentacruel",
    74: "Geodude",
    75: "Graveler",
    76: "Golem",
    77: "Ponyta",
    78: "Rapidash",
    79: "Slowpoke",
    80: "Slowbro",
    81: "Magnemite",
    82: "Magneton",
    83: "Farfetch'd",
    84: "Doduo",
    85: "Dodrio",
    86: "Seel",
    87: "Dewgong",
    88: "Grimer",
    89: "Muk",
    90: "Shellder",
    91: "Cloyster",
    92: "Gastly",
    93: "Haunter",
    94: "Gengar",
    95: "Onix",
    96: "Drowzee",
    97: "Hypno",
    98: "Krabby",
    99: "Kingler",
    100: "Voltorb",
    101: "Electrode",
    102: "Exeggcute",
    103: "Exeggutor",
    104: "Cubone",
    105: "Marowak",
    106: "Hitmonlee",
    107: "Hitmonchan",
    108: "Lickitung",
    109: "Koffing",
    110: "Weezing",
    111: "Rhyhorn",
    112: "Rhydon",
    113: "Chansey",
    114: "Tangela",
    115: "Kangaskhan",
    116: "Horsea",
    117: "Seadra",
    118: "Goldeen",
    119: "Seaking",
    120: "Staryu",
    121: "Starmie",
    122: "Mr. Mime",
    123: "Scyther",
    124: "Jynx",
    125: "Electabuzz",
    126: "Magmar",
    127: "Pinsir",
    128: "Tauros",
    129: "Magikarp",
    130: "Gyarados",
    131: "Lapras",
    132: "Ditto",
    133: "Eevee",
    134: "Vaporeon",
    135: "Jolteon",
    136: "Flareon",
    137: "Porygon",
    138: "Omanyte",
    139: "Omastar",
    140: "Kabuto",
    141: "Kabutops",
    142: "Aerodactyl",
    143: "Snorlax",
    144: "Articuno",
    145: "Zapdos",
    146: "Moltres",
    147: "Dratini",
    148: "Dragonair",
    149: "Dragonite",
    150: "Mewtwo",
    151: "Mew"
}

pokemonKeys = pokemonDict.keys()
pokemonNames = pokemonDict.values()
pokeDB = {}

def getDist(lat0,lon0,lat1,lon1):
    
    R = 6371000 #metres
    phi1 = math.radians(lat0)
    phi2 = math.radians(lat1)
    dPhi = math.radians(lat1-lat0)
    dLambda = math.radians(lon1-lon0)

    a = math.sin(dPhi/2) * math.sin(dPhi/2) + math.cos(phi1) * math.cos(phi2) * math.sin(dLambda/2) * math.sin(dLambda/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    d = R * c
    return int(round(d,0))

def sendPokefication(pokemon_id,lat,lon,poketime_utc,encounter_id):
    global time_db_check
        from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    
    time_now = datetime.utcnow()
    day_now = time_now.date()
    today   = str(day_now)
    
    time_1  = poketime_utc #timezone('UTC').localize(poketime_utc)
    time_0  = time_now #timezone('UTC').localize(time_now)
    
    if time_0 > time_1: return
    
    poketime = poketime_utc.replace(tzinfo=from_zone).astimezone(to_zone).strftime("%H:%M:%S")
    
    deltaTime   = time_1 - time_0
    dSeconds    = deltaTime.total_seconds()
    deltaMin    = int(dSeconds/60)
    deltaSec    = int((dSeconds - deltaMin*60))
    
    strMin      = str(deltaMin)
    strSec      = "0" + str(deltaSec) if deltaSec < 10 else str(deltaSec)
    pname = pokemonNames[pokemon_id-1]
    
    log.info("Found a wild {} that will disappear in {}m {}s".format(pname,strMin,strSec))
    
    
    
    seen_before = None
    try:
        seen_before = encounter_id in pokeDB
    except TypeError:
        seen_before = False
    
    
    
    for user in users.find():
        if not user.get('notify_list') or len(user.get('notify_list')) == 0: continue

        name = user.get('name')
        
        chat_id = user.get('chat_id')
        pokemonList = user.get('notify_list')
        paused = user.get('pause_notifications')
        uname = name if len(name) > 0 else chat_id
        location = user.get('location')
        
        if paused: continue
        
        if location and len(location) > 0:
            max_dist = user.get('max_distance')
            log.debug("Max_distance of user {} is {} m".format(uname,max_dist))
            max_dist = _max_ping_distance if not max_dist else int(max_dist)
            user_lat = location[0]
            user_lon = location[1]
            
            dist = getDist(float(lat),float(lon),float(user_lat),float(user_lon))
            if dist > _max_message_distance: continue
        
        if pname in pokemonList:
            street      = "Street"
            streetnum   = "no"
            
            #reverse geocode
            if not seen_before:
                user_gc_count = user.get('user_gc_count') if 'user_gc_count' in user else {}
                
                if not today in user_gc_count: user_gc_count[today] = 0
                
                log.debug("User {} has used {} geocodings today".format(uname,user_gc_count[today]))
                
                if user_gc_count[today] < _maxGC:
                    try:
                        geocode     = Geocoder.reverse_geocode(lat,lon)
                        street      = geocode.route
                        streetnum   = geocode.street_number
                        
                        if not streetnum: streetnum = "?"
                        pokeDB[encounter_id] = [street, streetnum,poketime_utc,pname,True]
                        log.info("{}: Encoded critter {} into db as: {} {}".format(encounter_id,pname,street, streetnum))
                        
                        gcCount = gc_counts.find()[0]
                        
                        if not today in gcCount: gcCount[today] = 0
                        
                        gcCount[today] += 1
                        user_gc_count[today] += 1
                        
                        log.info("Updated geocode-count: {} = {}".format(day_now,gcCount[today]))
                        
                        #db.update({'gc_counts':gcCount},eids=[1])
                        
                        users.update({'chat_id': chat_id},{"$set":{'user_gc_count':user_gc_count}})
                    except UnicodeEncodeError as e:
                        street      = str(round(lat,3))
                        streetnum   = str(round(lon,3))
                        pokeDB[encounter_id] = [street, streetnum,poketime_utc,pname,False]
                        log.warning("UnicodeEncodeError with pokemon {} at address {}, {}".format(pname,street,streetnum))
                    except GeocoderError as e:
                        street      = str(round(lat,3))
                        streetnum   = str(round(lon,3))
                        pokeDB[encounter_id] = [street, streetnum,poketime_utc,pname,False]
                        log.warning("Geocode-error: {} - using coords instead".format(e))
                    #except Exception as e:
                     #   street      = str(round(lat,3))
                      #  streetnum   = str(round(lon,3))
                       # pokeDB[encounter_id] = [street, streetnum,poketime_utc,pname,False]
                        #log.warning("Error: {} ".format(e))
                        
                else:
                    log.debug("User {} has over {} geocodes today, using coords instead".format(uname,user_gc_count[today]))
                    street      = pokeDB[encounter_id][0] if encounter_id in pokeDB else str(round(lat,3))
                    streetnum   = pokeDB[encounter_id][1] if encounter_id in pokeDB else str(round(lon,3))
            else:
                street = pokeDB[encounter_id][0] if encounter_id in pokeDB else "?"
                streetnum = pokeDB[encounter_id][1] if encounter_id in pokeDB else "?"
                log.info("Retrieved critter {} location name from DB as {}".format(pname,street+" "+streetnum))
            
            log.debug("Probing critter {} for user {}: Encounter-id: {}, seen-before: {},in db: {}".format(pname,uname,encounter_id,seen_before,encounter_id in pokeDB))
            
            custom_keyboard         = [['Pause','Location'],['Exclude ' + pname,]]
            reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True,resize_keyboard=True)
            
            if not seen_before:
                try:
                    location = user.get('location')
                    if location and len(location) > 0:
                        if dist and dist < max_dist:
                            bot.sendMessage(chat_id, text="A wild *{}* appeared {}m from you, it will disappear *{}* (in {}m {}s)".format(pname,dist,poketime,strMin,strSec),reply_markup=reply_markup,parse_mode=telegram.ParseMode.MARKDOWN)
                        if encounter_id in pokeDB and pokeDB[encounter_id][4]:
                            bot.sendVenue(chat_id,float(lat),float(lon),pname,"{} ({}m {}s)\r\r On {} {} ({} m away)".format(poketime,strMin,strSec,street,streetnum,dist),disable_notification=True,reply_markup=reply_markup,parse_mode=telegram.ParseMode.MARKDOWN)
                        else:
                            bot.sendVenue(chat_id,float(lat),float(lon),pname,"{} ({}m {}s)\r\r({} m away)".format(poketime,strMin,strSec,dist),disable_notification=True,reply_markup=reply_markup,parse_mode=telegram.ParseMode.MARKDOWN)
                    else:
                        bot.sendVenue(chat_id,float(lat),float(lon),pname,"{} ({}m {}s)\r\r {} {}".format(poketime,strMin,strSec,street,streetnum,),disable_notification=True,reply_markup=reply_markup,parse_mode=telegram.ParseMode.MARKDOWN)
                        
                    log.info("User {} has requested notification of {}: notification sent".format(uname,pname))
                except Unauthorized as e:
                    log.warning("Unable to send notification to user {}: {}".format(uname,e))
                    users.remove(User.chat_id == chat_id)
                    log.warning("Removed user {} from database".format(uname))
                except Exception as e:
                    log.warning("Unable to send notification to user {}: {}".format(uname,e))
                    continue
            else:
                log.info("Notification to {} not sent: already notified of {} on {}".format(uname,pname,street))
    
    if time_now > time_db_check + timedelta(seconds=60):
        log.info("Checking pokeDB for expired critters")
        log.debug("Size of encounter-db:{}".format(len(pokeDB)))
        time_db_check = time_now
        
        c = deepcopy(pokeDB)
        log.debug("Copied db: len = {}, type = {}".format(len(c),type(c)))
        for key, data in c.iteritems():
            try:
                time_poke = data[2]
                pokename = data[3]
            except IndexError as e:
                time_poke = time_now - timedelta(seconds=120)
                pokename = "Unknown pokemon"
                log.warn("Empty cell in pokeDB: {} = {}".format(key,data))
            deltaTime   = time_poke - time_now
            deltaMin    = round(deltaTime.seconds/60,0)
            log.debug("db: Critter {} expires {} or in {} mins".format(pokename,time_poke,deltaMin))
            if time_now > time_poke:
                pokeDB.pop(key,None)
                log.info("Deleted pokemon {} with encounter-id={} from pokeDB".format(pokename,key))
                
        c = None
    

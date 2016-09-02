#!/usr/bin/env python
from __future__ import division

# -*- coding: utf-8 -*-
#
# Simple Bot to send timed Telegram messages
# This program is dedicated to the public domain under the CC0 license.

"""
This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, StringCommandHandler, StringRegexHandler, MessageHandler, CommandHandler, RegexHandler, Filters, Job
from telegram.ext.dispatcher import run_async
from telegram import Location
import telegram
import logging
import time
import math
from time import mktime
from datetime import datetime, timedelta
import os, platform
import pprint
import re
from tinydb import TinyDB, Query, where
from tinydb.operations import delete
from tinydb_smartcache import SmartCacheTable
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import ConfigParser

from pogom import config

#from threading import Thread, Event
#from queue import Queue
#from flask_cors import CORS
#from pogom import config
#from pogom.app import Pogom
#from pogom.utils import get_args, insert_mock_data, get_encryption_lib_path
#from pogom.search import search_overseer_thread
#from pogom.models import init_database, create_tables, drop_tables, Pokemon, Pokestop, Gym
#from pgoapi import utilities as util
from pygeolib import GeocoderError 
from geopy.geocoders.base import GeocoderServiceError
from colorlog import ColoredFormatter
import colorlog
import pgoapi.exceptions
from pgoapi import PGoApi
from pymongo import MongoClient

varpath = 'var/'

# Enable logging
#coloredlogs.install(level='DEBUG')
logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
    filename= varpath + 'pokebot.log',
    filemode='w')
# define a Handler which writes INFO messages or higher to the sys.stderr

console =  colorlog.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = ColoredFormatter(
    '%(name)-12s: %(levelname)-8s %(message)s',
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

# tell the handler to use this format
console.setFormatter(formatter)
#console.addFilter(logging.Filter('waldo'))
#console.addFilter(logging.Filter('telegram'))
# add the handler to the root logger


#if len(logging.getLogger('').handlers) <= 1:
colorlog.getLogger('').addHandler(console)


# These are very noisey, let's shush them up a bit
logging.getLogger("peewee").setLevel(logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("pogom.pgoapi.pgoapi").setLevel(logging.WARNING)
logging.getLogger("telegram.bot").setLevel(logging.WARNING)
logging.getLogger("telegram.ext").setLevel(logging.WARNING)
logging.getLogger("JobQueue").setLevel(logging.WARNING)
logging.getLogger("pogom.pgoapi.rpc_api").setLevel(logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.ERROR)



# sys.setdefaultencoding() does not exist, here!
import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')


pp                          = pprint.PrettyPrinter(indent=4)

logger                      = logging.getLogger('pokebot')
job_queue                   = None
_listener                   = {} 
_serversteps                = {}
_serverdata                 = {}
defaultKeyboard             = ['Add', 'Remove', 'List'], ['Add server', 'Remove server'],['Location','Distance'],['Pause', 'Resume','Help']
pokemonList = {
    "001": "Bulbasaur",
    "002": "Ivysaur",
    "003": "Venusaur",
    "004": "Charmander",
    "005": "Charmeleon",
    "006": "Charizard",
    "007": "Squirtle",
    "008": "Wartortle",
    "009": "Blastoise",
    "010": "Caterpie",
    "011": "Metapod",
    "012": "Butterfree",
    "013": "Weedle",
    "014": "Kakuna",
    "015": "Beedrill",
    "016": "Pidgey",
    "017": "Pidgeotto",
    "018": "Pidgeot",
    "019": "Rattata",
    "020": "Raticate",
    "021": "Spearow",
    "022": "Fearow",
    "023": "Ekans",
    "024": "Arbok",
    "025": "Pikachu",
    "026": "Raichu",
    "027": "Sandshrew",
    "028": "Sandslash",
    "029": "Nidoran?",
    "030": "Nidorina",
    "031": "Nidoqueen",
    "032": "Nidoran?",
    "033": "Nidorino",
    "034": "Nidoking",
    "035": "Clefairy",
    "036": "Clefable",
    "037": "Vulpix",
    "038": "Ninetales",
    "039": "Jigglypuff",
    "040": "Wigglytuff",
    "041": "Zubat",
    "042": "Golbat",
    "043": "Oddish",
    "044": "Gloom",
    "045": "Vileplume",
    "046": "Paras",
    "047": "Parasect",
    "048": "Venonat",
    "049": "Venomoth",
    "050": "Diglett",
    "051": "Dugtrio",
    "052": "Meowth",
    "053": "Persian",
    "054": "Psyduck",
    "055": "Golduck",
    "056": "Mankey",
    "057": "Primeape",
    "058": "Growlithe",
    "059": "Arcanine",
    "060": "Poliwag",
    "061": "Poliwhirl",
    "062": "Poliwrath",
    "063": "Abra",
    "064": "Kadabra",
    "065": "Alakazam",
    "066": "Machop",
    "067": "Machoke",
    "068": "Machamp",
    "069": "Bellsprout",
    "070": "Weepinbell",
    "071": "Victreebel",
    "072": "Tentacool",
    "073": "Tentacruel",
    "074": "Geodude",
    "075": "Graveler",
    "076": "Golem",
    "077": "Ponyta",
    "078": "Rapidash",
    "079": "Slowpoke",
    "080": "Slowbro",
    "081": "Magnemite",
    "082": "Magneton",
    "083": "Farfetch'd",
    "084": "Doduo",
    "085": "Dodrio",
    "086": "Seel",
    "087": "Dewgong",
    "088": "Grimer",
    "089": "Muk",
    "090": "Shellder",
    "091": "Cloyster",
    "092": "Gastly",
    "093": "Haunter",
    "094": "Gengar",
    "095": "Onix",
    "096": "Drowzee",
    "097": "Hypno",
    "098": "Krabby",
    "099": "Kingler",
    "100": "Voltorb",
    "101": "Electrode",
    "102": "Exeggcute",
    "103": "Exeggutor",
    "104": "Cubone",
    "105": "Marowak",
    "106": "Hitmonlee",
    "107": "Hitmonchan",
    "108": "Lickitung",
    "109": "Koffing",
    "110": "Weezing",
    "111": "Rhyhorn",
    "112": "Rhydon",
    "113": "Chansey",
    "114": "Tangela",
    "115": "Kangaskhan",
    "116": "Horsea",
    "117": "Seadra",
    "118": "Goldeen",
    "119": "Seaking",
    "120": "Staryu",
    "121": "Starmie",
    "122": "Mr. Mime",
    "123": "Scyther",
    "124": "Jynx",
    "125": "Electabuzz",
    "126": "Magmar",
    "127": "Pinsir",
    "128": "Tauros",
    "129": "Magikarp",
    "130": "Gyarados",
    "131": "Lapras",
    "132": "Ditto",
    "133": "Eevee",
    "134": "Vaporeon",
    "135": "Jolteon",
    "136": "Flareon",
    "137": "Porygon",
    "138": "Omanyte",
    "139": "Omastar",
    "140": "Kabuto",
    "141": "Kabutops",
    "142": "Aerodactyl",
    "143": "Snorlax",
    "144": "Articuno",
    "145": "Zapdos",
    "146": "Moltres",
    "147": "Dratini",
    "148": "Dragonair",
    "149": "Dragonite",
    "150": "Mewtwo",
    "151": "Mew"
}

GlensList =["Aerodactyl", "Alakazam", "Arcanine", "Dragonair", "Arbok", "Articuno", "Chansey", "Charmeleon", "Dragonite", "Dratini", "Eevee", "Electrode", "Farfetch'd", "Flareon", "Growlithe", "Gyarados", "Hitmonchan", "Hitmonlee", "Jolteon", "Lapras", "Dewgong", "Lickitung", "Machamp", "Machoke", "Marowak", "Mew", "Mewtwo", "Moltres", "Muk", "Nidoking", "Nidoqueen", "Ninetales", "Omanyte", "Omastar", "Persian", "Pikachu", "Pinsir", "Ponyta", "Primeape", "Porygon", "Raichu", "Rapidash", "Scyther", "Snorlax", "Vaporeon", "Zapdos"]

def ping(host):
    """
    Returns True if host responds to a ping request
    """

    # Ping parameters as function of OS
    ping_str = "-n 1" if  platform.system().lower()=="windows" else "-c 1"

    # Ping
    return os.system("ping " + ping_str + " " + host) == 0
 
def start(bot, update):
    logger = logging.getLogger('poke' + "." + 'start')
    logger.debug("Entering start")
    
    chat_id = update.message.chat_id
    uname = update.message.chat.username
    
    if users.find({'chat_id': chat_id}).count() == 0:
        users.insert({'name' : uname, 'chat_id': chat_id, 'notify_list' : [],'server_list' : []})
        logger.info("Created new user with name = {} and with  {} entries".format(uname,users.find({'chat_id' : chat_id}).count()))
        
    custom_keyboard         = defaultKeyboard
    reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
    
    bot.sendMessage(update.message.chat_id, text='Hi! Welcome to pokembot. Use it to be notified when a pokemon appears close to you. This is still a work in progress so some things might be a little unstable, but now it should already work well enough to be useful.\n\nUse the following commands to manage what pokemons you want to be notified of: /add, /remove, /list\n\n Use /addserver and /removeserver to add and remove your own servers. Pokemons only appear when discovered by a scanning server, and in case there are no servers close to you, you may need to add one. To add a server you need a Pokemon Trainer Club account, which can be generated here:\n\nhttps://club.pokemon.com/us/pokemon-trainer-club/sign-up/\n\nIf the buttons don\'t work as expected, remember to use these commands. And hope you catch them all!',reply_markup=reply_markup)
  
def pause(bot, update):
    logger = logging.getLogger('poke' + "." + 'pause')
    logger.debug("Entering pause")
    
    chat_id = update.message.chat_id
    uname = update.message.chat.username
    
    custom_keyboard         = defaultKeyboard
    reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
    
    users.update({'chat_id': chat_id},{"$set":{'pause_notifications': True}})
    
    bot.sendMessage(update.message.chat_id, text='Notifications paused!',reply_markup=reply_markup)
  
def resume(bot, update):
    logger = logging.getLogger('poke' + "." + 'resume')
    logger.debug("Entering resume")
    
    chat_id = update.message.chat_id
    uname = update.message.chat.username
    
    custom_keyboard         = defaultKeyboard
    reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
    
    users.update({'chat_id': chat_id},{"$set":{'pause_notifications': False}})
    
    bot.sendMessage(update.message.chat_id, text='Notifications resumed.',reply_markup=reply_markup)
  
def addpokemon(bot, update,args):
    
    logger = logging.getLogger('poke' + "." + 'add')
    logger.debug("Entering add: args = {}".format(args))
    
    chat_id = update.message.chat_id
    uname = update.message.chat.username
    global _listener
    
    if args is not None and len(args) > 0:
        logger.debug("args = {}, args[0] = {}".format(args,args[0]))
        if args[0] == 'Add ALL':
            selectedList = []
            for poke in pokemonList.values():
                selectedList.append(poke)
                users.update({'chat_id': chat_id},{"$set":{'notify_list': selectedList}})
                
            custom_keyboard         = defaultKeyboard
            reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
            bot.sendMessage(chat_id, text="Ok, added all pokemons to the notify list",reply_markup=reply_markup)
            return
        elif args[0] == 'Glen':
            selectedList = []
            for poke in GlensList:
                selectedList.append(poke)
                users.update({'chat_id': chat_id},{"$set":{'notify_list': selectedList}})
                                
            custom_keyboard         = defaultKeyboard
            reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
            bot.sendMessage(chat_id, text="Ok, added the Glen's List (TM) selection to the notify list",reply_markup=reply_markup)
            return
            
        poke = args[0]
        if poke in pokemonList.values():
            
            selectedList = list(users.find({'chat_id' : chat_id},{'notify_list': 1, '_id': 0}))[0]['notify_list']

            if not poke in selectedList:
                selectedList.append(poke)
                users.update({'chat_id': chat_id},{"$set":{'notify_list': selectedList}})
                logger.info("{}: Added pokemon '{}' to notify-list".format(uname,poke))
                
                #custom_keyboard         = [['Cancel', 'ADD ALL']]
                
                #alphaList = sorted(pokemonList.values())
                #for pokename in alphaList:  
                    #if not pokename in selectedList:
                        #custom_keyboard.append([pokename])
                
                #reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=False)
                bot.sendMessage(chat_id, text="Added pokemon '{}' to notify list".format(poke))
                
                
                
            else:
                logger.info("Pokemon '{}' is already in notify-list".format(poke))
                bot.sendMessage(chat_id, text="Pokemon '{}' is already in notify-list".format(poke))
        else:
            logger.warning("Didn't find any pokemon called '{}'".format(poke))
            bot.sendMessage(chat_id, text="Didn't find any pokemon called '{}'".format(poke))
        
    else:   
        alphaList = sorted(pokemonList.values())
        selectedList = list(users.find({'chat_id' : chat_id},{'notify_list': 1, '_id': 0}))[0]['notify_list']
        #print "T: {}, L: {}, D = {}".format(type(selectedList),len(selectedList),selectedList)
        
        custom_keyboard         = [['Cancel', 'Add ALL','Glen\'s List']]
        for pokename in alphaList:  
            if not pokename in selectedList:
                custom_keyboard.append([pokename])
                
        reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=False)
        
        bot.sendMessage(chat_id, text="Enter pokemon to add to notify list:",reply_markup=reply_markup)
        _listener[uname] = 'addpokemon'
        
        logger.debug("Set listener of {} to: {}".format(uname,_listener[uname] if uname in _listener else "?"))
          
def removepokemon(bot, update,args):
    logger = logging.getLogger('poke' + "." + 'remove')
    logger.debug("Entering remove: args = {}".format(args))
    global _listener
    
    chat_id = update.message.chat_id
    uname = update.message.chat.username
    
    selectedList = list(users.find({'chat_id' : chat_id},{'notify_list': 1, '_id': 0}))[0]['notify_list']
        
    if len(selectedList) == 0:
        bot.sendMessage(chat_id, text="Pokemon list empty!")
        return
    
    custom_keyboard         = [['Cancel','REMOVE ALL']]
    for pokename in selectedList:
        custom_keyboard.append([pokename])
    reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=False)
    
    bot.sendMessage(chat_id, text="Remove pokemon from notify list:",reply_markup=reply_markup)
    _listener[uname] = 'removepokemon'
    logger.debug("Set listener of {} to: {}".format(uname,_listener[uname] if uname in _listener else "?"))
    
    if args is not None and len(args) > 0:
        if args[0] == 'REMOVE ALL':
            selectedList = []
            users.update({'chat_id': chat_id},{"$set":{'notify_list': selectedList}})
            custom_keyboard         = defaultKeyboard
            reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
            bot.sendMessage(chat_id, text="Ok, emptied the whole list",reply_markup=reply_markup)
            return
                
        
        poke = args[0]
        if poke in selectedList: 
            selectedList.remove(poke)
            users.update({'chat_id': chat_id},{"$set":{'notify_list': selectedList}})
            
            custom_keyboard         = [['Cancel','REMOVE ALL']]
            for pokename in selectedList:
                custom_keyboard.append([pokename])
            reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=False)
            bot.sendMessage(chat_id, text="{}' removed".format(poke),reply_markup=reply_markup)
            
def listpokemon(bot, update):
    logger = logging.getLogger('poke' + "." + 'list')
    logger.debug("Entering list pokemon")
    
    chat_id = update.message.chat_id
    uname = update.message.chat.username
    
    selectedList = list(users.find({'chat_id' : chat_id},{'notify_list': 1, '_id': 0}))[0]['notify_list']
    
    custom_keyboard         = defaultKeyboard
    reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
    
    bot.sendMessage(chat_id, text="Currently notifying of following Pokemons:\n\n" + '\n'.join(sorted(selectedList)),reply_markup=reply_markup) 
   
def setlocation(bot, update,args):
    logger = logging.getLogger('poke' + "." + 'setlocation')
    
    chat_id = update.message.chat_id
    uname = update.message.chat.username
    global _listener
    
    logger.debug("message = {}".format(update.message))
    
    reply_markup    =  telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton('Send my location', request_contact=None,request_location=True)]], one_time_keyboard=True,resize_keyboard=True)
    bot.sendMessage(chat_id, text="If you share your location, we can calculate distance to nearby pokemons",reply_markup=reply_markup,)

def setdistance(bot, update,args):
    logger = logging.getLogger('poke' + "." + 'setdistance')
    
    chat_id = update.message.chat_id
    uname = update.message.chat.username
    global _listener
    
    if args is not None and len(args) > 0:
        max_dist = args[0]
        
        users.update({'chat_id': chat_id},{"$set":{'max_distance': max_dist}})
        custom_keyboard         = defaultKeyboard
        reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
        bot.sendMessage(chat_id, text="Set maximum distance to {} m".format(max_dist),reply_markup=reply_markup)
        _listener[uname] = None
        return
    else:
        bot.sendMessage(chat_id, text="Notify of pokemons how far from you? Enter the distance in meters (default=2000)\r\r(Pokemons further away will still show up as a message but there will be no notification on iOS and silent on android)")
        _listener[uname] = 'setdistance'
    
def addserver(bot, update):
    
    logger = logging.getLogger('poke' + "." + 'addserver')
    logger.debug("Entering add server")
    
    chat_id = update.message.chat_id
    uname = update.message.chat.username
    global _listener
    global _serversteps
    
    _listener[uname] = 'addserver'
    
    def test_func(val):
        return len(val) > 0
        
    num_servers = 0
    userlist = users.find()
    
    for user in userlist:
        serverList = user.get('server_list') 
        logger.debug("User {} has {} servers".format(user.get('name'),len(serverList)))
        logger.debug("list = {}".format(serverList))
        num_servers += len(serverList)
    
    if num_servers >= 50:
        _listener[uname] = None
        custom_keyboard         = defaultKeyboard
        reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
        bot.sendMessage(chat_id, text="At this time, only 50 servers can be supported. Please hold on while we try to get a better host",reply_markup=reply_markup)
        return
        
    if not uname in _serverdata: _serverdata[uname] = {}
    
    if not uname in _serversteps: _serversteps[uname] = None
    
    if _serversteps[uname] is None:
        
        bot.sendMessage(chat_id, text="Note: adding own servers is for now a bit unstable, but feel free to proceed. Niantic added a step that the user also needs to accept the terms of service aftrer logging in.\n\nYou will need to enter the login credentials of a pokemon trainer account, it is not advised to use the same one that you're playing with. PTC accounts can be generated here:\n https://club.pokemon.com/us/pokemon-trainer-club/sign-up/\n\n Please enter login:")
        _serversteps[uname] = 1
    elif _serversteps[uname] == 1:
        bot.sendMessage(chat_id, text="Please enter login:")
    elif _serversteps[uname] == 2:
        bot.sendMessage(chat_id, text="Please enter password:")
    elif _serversteps[uname] == 3:
        bot.sendMessage(chat_id, text="Please enter location (it can be name such as 'Paris' or coordinates separated by space, such as '48.84 2.33':")
    elif _serversteps[uname] == 4:
        bot.sendMessage(chat_id, text="Please enter number of steps (one step equals about 70m), default=12")
    elif _serversteps[uname] == 5:
        bot.sendMessage(chat_id, text="Please enter delay between scans in seconds, default=10")
    else:
        custom_keyboard         = defaultKeyboard
        reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
        bot.sendMessage(chat_id, text="Not implemented yet!",reply_markup=reply_markup) 
    
def removeserver(bot, update, args):

    logger = logging.getLogger('poke' + "." + 'removeserver')
    logger.debug("Entering remove server")
    global _listener
    
    chat_id = update.message.chat_id
    uname = update.message.chat.username
    
    serverList = users.find({'chat_id' : chat_id}).get('server_list')
    if not serverList: serverList = {}
    
    if len(serverList) == 0:
        custom_keyboard         = defaultKeyboard
        reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
        bot.sendMessage(chat_id, text="No servers registered on your name!",reply_markup=reply_markup)
        return
    
    custom_keyboard         = [['Cancel']]
    for servername in serverList:
        custom_keyboard.append([servername])
    
    reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=False)
    
    bot.sendMessage(chat_id, text="Choose server to remove:",reply_markup=reply_markup) 
    _listener[uname] = "removeserver"
    
    if args is not None and len(args) > 0:
        serv = args[0]
        logger.debug("Remove: list = {}, server = {}".format(serverList,serv))
        if serv in serverList: 
            del serverList[serv]
            
            users.update({'chat_id': chat_id},{"$set":{'server_list': serverList}})
            
            custom_keyboard         = [['Cancel']]
            for servername in serverList:
                custom_keyboard.append([servername])
            reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=False)
            bot.sendMessage(chat_id, text="{}' removed".format(serv),reply_markup=reply_markup)
            
            if len(serverList) == 0:
                custom_keyboard         = defaultKeyboard
                reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
                bot.sendMessage(chat_id, text="No servers left to remove",reply_markup=reply_markup)
                return
            
def startserver(bot, update):
    logger = logging.getLogger('poke' + "." + 'startserver')
    logger.debug("Starting server")
    
    global _listener
    global _serversteps
    global _serverdata
    
    chat_id = update.message.chat_id
    uname = update.message.chat.username
    login = _serverdata[uname][1]
    passwd = _serverdata[uname][2]
    
    serverList = list(users.find({'chat_id' : chat_id},{'server_list': 1, '_id': 0}))[0]['server_list']
    if not serverList: serverList = {}
    
    serverList[login] = _serverdata[uname]
    users.update({'chat_id': chat_id},{"$set":{'server_list': serverList}})
    
    custom_keyboard         = defaultKeyboard
    reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
    
    bot.sendMessage(chat_id, text="Starting server with username = {}".format(login),reply_markup=reply_markup)
    
    try:
        api = PGoApi()
        api.set_authentication(provider='ptc', username=login, password=passwd)
        pos = _serverdata[uname][3].split()
        
        api.set_position(pos[0],pos[1],0)
        pos2 = api.get_position()
        logger.debug("Position for {} is set as {},{}".format(login,pos2[0],pos2[1]))
        if not pos2[0]: raise ValueError("server did not return position data")

    except pgoapi.exceptions.AuthException as e:          
        logger.error('Failed to login to Pokemon Go with account {}: AuthException:{}'.format(login,e))
        bot.sendMessage(chat_id, text='Failed to login to Pokemon Go with account {}: {}'.format(login,e),reply_markup=reply_markup)
        return
    except ValueError as e:
        logger.error('Failed to login to Pokemon Go with account {}: {}'.format(login,e))
        bot.sendMessage(chat_id, text='Failed to login to Pokemon Go with account {}: {}'.format(login,e),reply_markup=reply_markup)
        return
    except Exception as e:
        logger.error('Failed to login to Pokemon Go with account {}: Error:{}'.format(login,e))
        bot.sendMessage(chat_id, text='Failed to login to Pokemon Go with account {}: {}'.format(login,e),reply_markup=reply_markup)
        return
    finally:
        _listener[uname] = None
        _serversteps[uname] = None
        _serverdata[uname] = {}
    logger.info('Login for account {} successful!'.format(login))
    bot.sendMessage(chat_id, text='Login for account {} successful'.format(login),reply_markup=reply_markup)
    
    
def help(bot, update):

    logger = logging.getLogger('poke' + "." + 'help')
    logger.debug("Entering help")
    
    chat_id = update.message.chat_id
    uname = update.message.chat.username
    
    custom_keyboard         = defaultKeyboard
    reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
    
    bot.sendMessage(chat_id, text="Use the following commands to manage what pokemons you want to be notified of: _/add_, _/remove_, /list\n\n Use /addserver and /removeserver to add and remove your own servers. Pokemons only appear when discovered by a scanning server, and in case there are no servers close to you, you may need to add one. To add a server you need a Pokemon Trainer Club account, which can be generated here:\n\nhttps://club.pokemon.com/us/pokemon-trainer-club/sign-up/\n\nIf the buttons don\'t work as expected, remember to use these commands. And hope you catch them all!",reply_markup=reply_markup,parse_mode=telegram.ParseMode.MARKDOWN)
    
def cli_noncommand(bot, update):
    """
    You can also get the update queue as an argument in any handler by
    appending it to the argument list. Be careful with this though.
    Here, we put the input string back into the queue, but as a command.
    To learn more about those optional handler parameters, read:
    http://python-telegram-bot.readthedocs.org/en/latest/telegram.dispatcher.html
    """
    global _listener
    global _serversteps
    global _serverdata
    
    chat_id = update.message.chat_id
    uname = update.message.chat.username
    
    logger = logging.getLogger('poke' + "." + 'noncommand')
    logger.debug("Noncommand: user = {}, listener = {}".format(uname,_listener[uname] if uname in _listener else "?"))
    
    text = '%s' % update.message.text
    #reply_markup        = telegram.ReplyKeyboardHide()
    logger.debug("Noncommand with the text = {}".format(text))
    
    if text == 'Cancel' or text == 'cancel':
        
        chat_id = update.message.chat_id
        
        _listener[uname] = None
        custom_keyboard         = defaultKeyboard
        reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
        bot.sendMessage(chat_id, text="Ok!",reply_markup=reply_markup)
    elif text == 'Add':
        addpokemon(bot, update, [])
    elif text == 'Remove':
        removepokemon(bot, update, [])
    elif text == 'List':
        listpokemon(bot, update)
    elif text == 'Help':
       help(bot, update)
    elif text == 'Location':
       setlocation(bot, update,[])
    elif text == 'Distance':
       setdistance(bot, update,[])
    elif text == 'Add server':
        _serversteps[uname] = None
        addserver(bot, update)
    elif text == 'Remove server':
        removeserver(bot, update, [])
    elif text == 'Pause':
        pause(bot, update)
    elif text == 'Resume':
        resume(bot, update)
    elif text.startswith('Exclude'):
        words = text.split()
        removepokemon(bot, update, [words[1]])
    else:   
        if uname in _listener and _listener[uname] == "addpokemon":
            if text.startswith('Glen'):
                addpokemon(bot, update, ["Glen"])
            else:
                addpokemon(bot, update, [text])
        elif uname in _listener and _listener[uname] == "removepokemon":
            removepokemon(bot, update, [text])
        elif uname in _listener and _listener[uname] == "removeserver":
            removeserver(bot, update, [text])
        elif uname in _listener and _listener[uname] == "setdistance":
            setdistance(bot, update, [text])
        elif uname in _listener and _listener[uname] == 'addserver':
            if text is not None and len(text) > 0:
                if text == 'Next' or text == "next":
                    _serversteps[uname] += 1
                    addserver(bot, update)
                elif text == "Edit" or text == "edit":
                    addserver(bot, update)
                elif text == "Finish" or text == "finish":
                    startserver(bot, update)
                elif text == 'Advanced' or text == 'advanced':
                    _serversteps[uname] += 1
                    addserver(bot, update)
                else:
                    prompt = ""
                    custom_keyboard         = [['Next', 'Edit'], ['Cancel']]
                    if _serversteps[uname] == 1:
                        prompt = "login:"
                        custom_keyboard         = [['Next', 'Edit'], ['Cancel']]
                    elif _serversteps[uname] == 2:
                        prompt = "password:"
                        custom_keyboard         = [['Next', 'Edit'], ['Cancel']]
                    elif _serversteps[uname] == 3:
                        prompt = "location: "
                        custom_keyboard         = [['Finish', 'Edit','Advanced'],['Cancel']]
                    elif _serversteps[uname] == 4:
                        prompt = "step count:"
                        custom_keyboard         = [['Finish', 'Next','Edit'],['Cancel']]
                    elif _serversteps[uname] == 5:
                        prompt = "scan delay:"
                        custom_keyboard         = [['Finish', 'Edit'],['Cancel']]
                    if _serversteps[uname] is not None:
                        _serverdata[uname][_serversteps[uname]] = text
                    if _serversteps[uname] == 3:
                        logger.debug("{} - Step 3: text = {}".format(uname,text))
                        if len(text) > 0:
                            # use lat/lng directly if matches such a pattern
                            prog = re.compile("^(\-?\d+\.\d+),?\s?(\-?\d+\.\d+)$")
                            res = prog.match(text)
                            if res:
                                logger.debug('Using coordinates from CLI directly')
                                position = (float(res.group(1)), float(res.group(2)), 0)
                            else:
                                try:
                                    logger.debug('Looking up coordinates in API')
                                    position = util.get_pos_by_name(text)
                                except GeocoderServiceError as e:
                                    logger.warn('GeocoderServiceError: {}'.format(e))
                                    bot.sendMessage(chat_id, text="GeocoderServiceError: {}. Please use coordinates instead".format(e))
                                    _serversteps[uname] = 3
                                    addserver(bot, update)
                                    return
                                except GeocoderError as e:
                                    logger.warn('GeocoderError: {}'.format(e))
                                    bot.sendMessage(chat_id, text="GeocoderError: {}. Please use coordinates instead".format(e))
                                    _serversteps[uname] = 3
                                    addserver(bot, update)
                                    return
                                except Exception as e:
                                    logger.warn('Error: {}'.format(e))
                                    bot.sendMessage(chat_id, text="Error: {}. Please use coordinates instead".format(e))
                                    _serversteps[uname] = 3
                                    addserver(bot, update)
                                    return
                                    
                            pos = position
                            pos = text.split(" ")
                            lat = pos[0]
                            lon = pos[1]
                            bot.sendLocation(chat_id, float(lat),float(lon))
                            logger.debug("text = {}, lat = {}, lon = {}".format(text,lat,lon))
                            
                    logger.debug("Serverdata: {}".format(_serverdata[uname]))
                    reply_markup            = telegram.ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
                    bot.sendMessage(chat_id, text="Confirm step {}: {} = {}".format(_serversteps[uname],prompt,text),reply_markup=reply_markup)
                    
                    
        else:
            logger.info("CLI-command: {}".format(text))

def location_received(bot, update):
    logger = logging.getLogger('poke' + "." + 'location')
    
    chat_id = update.message.chat_id
    uname = update.message.chat.username
    uname = uname if len(uname) > 0 else chat_id
    
    logger.debug("Received Location from user: {}".format(uname))
    
    lat = update.message.location.latitude
    lon = update.message.location.longitude
    
    location = [lat,lon]
    
    if len(location) > 0:
        users.update({'chat_id': chat_id},{"$set":{'location':location}})
        
        bot.sendMessage(chat_id=update.message.chat_id, text="Location added to user \'{}\'".format(uname))
        logger.info("User {} added location: {}, {}".format(uname,lat,lon))
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text="Failed to process location of user \'{}\'".format(uname))
      
def unknown(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

def main():
    
    
    logger = logging.getLogger('pokebot' + "." + 'main')
    logger.info("Entering main")
    global job_queue
    global users
    global gc_counts
    global db
    
    botconfig = ConfigParser.RawConfigParser()
    botconfig.read('config/bot.ini')
    
    TOKEN = botconfig.get('telegram', 'token')
    URI = botconfig.get('pymongo', 'uri')
    
    client = MongoClient(URI)
    db = client.pogom
    
    users = db.users
    gc_counts = db.gc_counts
    
    print "Google-geocode counts:"
    
    for key,item in gc_counts.find()[0].items():
        print "--> {}: {}".format(key,item)
    
    
    updater = Updater(TOKEN,workers=10)
    job_queue = updater.job_queue
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("add", addpokemon,pass_args=True))
    dp.add_handler(CommandHandler("remove", removepokemon,pass_args=True))
    dp.add_handler(CommandHandler("list", listpokemon))
    dp.add_handler(CommandHandler("pause", pause))
    dp.add_handler(CommandHandler("resume", resume))
    dp.add_handler(CommandHandler("addserver", addserver,pass_args=False))
    dp.add_handler(CommandHandler("setlocation", setlocation,pass_args=True))
    dp.add_handler(CommandHandler("setdistance", setdistance,pass_args=True))
    dp.add_handler(CommandHandler("removeserver", removeserver,pass_args=True))
    dp.add_handler(RegexHandler('[^/].*', cli_noncommand), group=1)
    dp.add_handler(MessageHandler([Filters.location], location_received))
    dp.add_handler(MessageHandler([Filters.command], unknown))
    
    # log all errors
    #dp.add_error_handler(error)
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
       
    # Start the Bot
    updater.start_polling(poll_interval=2.0, timeout=90)
        
    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    
    num_users = 0
        
    num_servers = 0
    
    for user in users.find():
        num_users += 1
        serverList = user.get('server_list') if 'server_list' in user else []
        logger.debug("User {} has {} servers".format(user.get('name'),len(serverList)))
        num_servers += len(serverList)
    
    logger.info ("Started pokembot successfully on: {}".format(time_now))
    logger.info("Database contains {} accounts and {} servers".format(num_users,num_servers))
        
    updater.idle()

if __name__ == '__main__':
    main()

class LoginError(Exception):
    logger.error("Login Error")
    pass
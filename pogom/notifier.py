import json
from pushbullet import Pushbullet
from datetime import datetime
from motionless import AddressMarker, DecoratedMap, CenterMap, VisibleMap
import sys


# Fixes the encoding of the male/female symbol
reload(sys)
sys.setdefaultencoding('utf8')

pushbullet_client = None
wanted_pokemon = None
unwanted_pokemon = None
pb_api = "o.J76nZOWJiLOHbvE8fGBc2lfwc3ma4mi5"

# Initialize object
def init():
    global pushbullet_client, wanted_pokemon, unwanted_pokemon
    # load pushbullet key
    # with open('config.json') as data_file:
        # data = json.load(data_file)
        # # get list of pokemon to send notifications for
        # if "notify" in data:
            # wanted_pokemon = _str( data["notify"] ) . split(",")

            # # transform to lowercase
            # wanted_pokemon = [a.lower() for a in wanted_pokemon]
        # #get list of pokemon to NOT send notifications for
        # if "do_not_notify" in data:
            # unwanted_pokemon = _str( data["do_not_notify"] ) . split(",")

            # # transform to lowercase
            # unwanted_pokemon = [a.lower() for a in unwanted_pokemon]
        # get api key
    api_key = pb_api
    if api_key:
        pushbullet_client = Pushbullet(api_key)


# Safely parse incoming strings to unicode
def _str(s):
  return s.encode('utf-8').strip()

  

  
  
# Notify user for discovered Pokemon
def pokemon_found(pokename, lat, lon, disapper_time):
    #pushbulley channel 
    # Or retrieve a channel by its channel_tag. Note that an InvalidKeyError is raised if the channel_tag does not exist
    #my_channel = pushbullet_client.get_channel('pokefinderhenning')  
    my_channel = pushbullet_client.channels[0]
    # get name
    # pokename = _str(pokemon["name"]).lower()
    # check array
    # if not pushbullet_client:
        # return
    # elif wanted_pokemon != None:
        # if not pokemon in wanted_pokemon:
            # return
    # elif wanted_pokemon == None and unwanted_pokemon != None:
        # if pokename in unwanted_pokemon:
            # return
    # notify
    print "[+] Notifier found pokemon:", pokename

    latLon = '{},{}'.format(repr(lat), repr(lon))

  #  disappear_time = str(datetime.fromtimestamp(pokemon["disappear_time"] + 7200).strftime("%H:%M").lstrip('0'))
    notification_text = _str(pokemon["name"]) + "! Bis " + disappear_time + "!"

    mappos = "https://maps.googleapis.com/maps/api/staticmap?center=" + repr(lat) + "," + repr(lon) + "&zoom=15&size=300x300&markers=color:red%7Clabel:A%7C" + repr(lat) + "," + repr(lon)
    maptext = notification_text + "\n" + "Overview: http://merklinger.synology.me:9785"

#    location_text = "Preview: " + dmap.generate_url()
#    push = my_channel.push_link(notification_text, google_maps_link, body=location_text)
#    print dmap.generate_url()
    pushmap = my_channel.push_file(file_url = mappos, file_name=notification_text, file_type="image/png", body=maptext)
    #push = pushbullet_client.push_link(notification_text, google_maps_link, body=location_text)



init()

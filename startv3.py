import os
import re
import time
import socket

acc_fname = "config/acc.csv"
places_fname = "config/places.csv"

acc_regex = "([^;]+);([^;]+);([^;]+);(.*)"
places_regex = "([^;]+);([^;]+);([^;]+);([^;]+);(.*)"

accounts = []
places = []

windows = (os.name == 'nt')
if windows:
    print "detected windows as the OS"

with open(acc_fname, "r") as ins:
    firstline = True
    for line in ins:
        if firstline:
            firstline = False
            continue
            
        line = line.rstrip() #replace that newline char
        
        account = {}
        m = re.search(acc_regex, line)
        account["login"] = m.group(1)
        account["pw"] = m.group(2)
        account["auth"] = m.group(3)
        account["suspended"] = m.group(4)
        if not account["suspended"].startswith("X"):
            accounts.append(account)

with open(places_fname, "r") as ins:
    firstline = True
    for line in ins:
        if firstline:
            firstline = False
            continue
            
        line = line.rstrip() #replace that newline char
        
        place = {}
        m = re.search(places_regex, line)
        place["lat"] = m.group(1)
        place["lng"] = m.group(2)
        place["steps"] = m.group(3)
        place["delay"] = m.group(4)
        place["description"] = m.group(5)
        places.append(place)

x = 0
try:
    hostname = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com",80))
        hostname = s.getsockname()[0]
        s.close()
    except Exception as e:
        hostname = "unknown_host%s" % ( str(id(e)) )
    
    for place in places:
        #print place
        #print accounts[x]
        
        account = accounts[x]
        status_name = "worker%d@%s" % ( x, hostname )
        #exe = "start cmd /k python runserverv2.py -ns -a %s -u %s -p %s -ss %s" % (auth, login, pw, fname)
        execute = "python runserver.py -ns -a %s -u %s -p %s -ss spawns_%d.json -l \"%s,%s\" -st %s -sd %s --dump-spawnpoints -sn %s" % \
                    (account["auth"], account["login"], account["pw"], x, place["lat"], place["lng"], place["steps"], place["delay"], status_name)
        
        print("executing '%s' for Location '%s'" % (execute, place["description"]))
        if windows:
            os.system("start cmd /k %s" % execute)
        else:
            os.system("screen -AmdS pkmn_worker%d-thread %s" % (x, execute))
        
        x = x + 1
        time.sleep(1)
except IndexError as e:
    print "no more accounts found! skipping"
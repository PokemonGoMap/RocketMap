import os
import re
import time
import socket

acc_fname = "config/acc.csv"
places_fname = "config/places.csv"

acc_regex = "([^;]+);([^;]+);([^;]+);(.*)"
places_regex = "([^;]+);([^;]+);([^;]+);(.*)"

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
            
        line = line[:-1] #replace that newline char
        
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
        
        place = {}
        m = re.search(places_regex, line)
        place["lat"] = m.group(1)
        place["lng"] = m.group(2)
        place["steps"] = m.group(3)
        place["description"] = m.group(4)
        places.append(place)
            
            
hostname = None
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com",80))
    hostname = s.getsockname()[0]
    s.close()
except Exception as e:
    hostname = "unknown_host%s" % ( str(id(e)) )

x = 0
accountNumber = len( accounts )
for place in places:
    if not f.endswith( compressedEnding ):
        continue
    #print place
    #print accounts[x]
    
    fileName = base_dir + f
    
    account = accounts[x]
    status_name = "@%s_spiral%d" % ( hostname, x )
    #exe = "start cmd /k python runserverv2.py -ns -a %s -u %s -p %s -ss %s" % (auth, login, pw, fname)
    execute = "python runserver.py -ns -a %s -u %s -p %s -sn %s -l \"%s,%s\" -st %s" % \
                (account["auth"], account["login"], account["pw"], status_name, place["lat"], place["lng"], place["steps"])
    
    print("executing '%s'" % ( execute ))
    if windows:
        os.system("start cmd /k %s" % execute)
    else:
        os.system("screen -AmdS pkmn_worker%d-thread %s" % (x, execute))
    
    x = x + 1
    if( x >= accountNumber ):
        print "no more accounts found! skipping"
        exit(0)
    time.sleep(8)
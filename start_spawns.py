import os
import re
import time
import socket

acc_fname = "config/acc.csv"

acc_regex = "([^;]+);([^;]+);([^;]+);(.*)"

accounts = []

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


hostname = None
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com",80))
    hostname = s.getsockname()[0]
    s.close()
except Exception as e:
    hostname = "unknown_host%s" % ( str(id(e)) )

base_dir = "spawns/"
compressedEnding = ".compressed.json"
x = 0
accountNumber = len( accounts )
for f in os.listdir( base_dir ):
    if not f.endswith( compressedEnding ):
        continue
    #print accounts[x]
    
    fileName = base_dir + f
    
    account = accounts[x]
    status_name = "@%s_worker%d" % ( hostname, x )
    execute = "python runserver.py -ns -a %s -u %s -p %s -ss %s -sn %s" % \
                (account["auth"], account["login"], account["pw"], fileName, status_name)
    
    print("executing '%s'" % ( execute ))
    if windows:
        os.system("start cmd /k %s" % execute)
    else:
        os.system("screen -AmdS pkmn_worker%d-thread %s" % (x, execute))
    
    x = x + 1
    if( x >= accountNumber ):
        print "no more accounts found! skipping"
        exit(0)
    time.sleep(5)
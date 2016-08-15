import os
import re

acc_fname = "config/only_acc.csv"
regex = "(.*);(.*);(.*);(.*)"
jsonname = "spawns/spawns_ID.json"

with open(acc_fname, "r") as ins:
    firstline = True
    x = 0
    for line in ins:
        if firstline:
            firstline = False
            continue
    
        m = re.search(regex, line)
        login = m.group(1)
        pw = m.group(2)
        auth = m.group(3)
        suspended = m.group(4)
        
        fname = jsonname.replace("ID", str(x))
        
        if not suspended and os.path.isfile(fname):
            exe = "screen -AmdS pkmn-worker%s-thread python runserverv2.py -ns -a %s -u %s -p %s -ss %s" % (x, auth, login, pw, fname)
            
            os.system("echo executing '%s'" % exe)
            os.system(exe)
            
            x = x + 1
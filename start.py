import os
import re

fname = "config/acc.csv"
regex = "(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*)"

with open(fname, "r") as ins:
    array = []
    x = 0
    for line in ins:
        array.append(line)
        
        id = x
        x = x + 1
        
        if id == 0:
            continue
    
        m = re.search(regex, line)
        login = m.group(1)
        pw = m.group(2)
        auth = m.group(3)
        steps = int(m.group(4))
        lat = float(m.group(5))
        long = float(m.group(6))
        delay = int(m.group(7))
        desc = m.group(8)
        str = "screen -AmdS pkmn-worker%s-thread python runserver.py --no-server -st %d -a %s -u %s -p %s -l \"%f,%f\" -sd %d" % (id, steps, auth, login, pw, lat, long, delay)
        
        os.system("echo executing '%s'" % str)
        os.system(str)
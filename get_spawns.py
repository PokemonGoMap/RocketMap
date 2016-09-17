import os
import re
import time
import subprocess
import signal

places_fname = "config/places.csv"

acc_regex = "([^;]+);([^;]+);([^;]+);(.*)"
places_regex = "([^;]+);([^;]+);([^;]+);(.*)"

places = []


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

maxTries = 15
waittime = 1

x = 0

for place in places:
    spawnfile = "spawns/spawns_%d.json" % ( x )
    position = "%s,%s" % ( place["lat"], place["lng"] )
    steps = place["steps"]
    arguments = [ "python", "runserver.py", "-ns", "-ss", spawnfile, "--dump-spawnpoints", "-l", position, "-st", steps, "-sd", "1000", "-u", "kek", "-p", "lel" ]
    
    if( os.path.isfile( spawnfile ) ):
        print( "removing old file '%s'" % ( spawnfile ) )
        os.remove( spawnfile )
    
    print("executing '%s' for Location '%s'" % ( arguments, place["description"]) )
    
    app = subprocess.Popen( args=arguments )
    
    tryCount = 1
    lastFileSize = None
    while True:
        if( os.path.isfile( spawnfile ) ):
            statinfo = os.stat( spawnfile )
            fileSize = statinfo.st_size
            if( lastFileSize == None ):
                lastFileSize = fileSize
            else:
                if( ( fileSize > 0 ) and ( fileSize == lastFileSize ) ):
                    break
                else:
                    lastFileSize = fileSize
        
        if( tryCount > maxTries ):
            raise Exception( "Too much tries, still no JSON file created..stopping this thing....are you even connected? kek" )
            
        tryCount += 1
        
        time.sleep(waittime)
    
    if app.poll() == None:
        #process still running..
        time.sleep(waittime) #waiting one more time, just to be safe..
        
        os.kill( app.pid, signal.SIGTERM )
    
    x = x + 1
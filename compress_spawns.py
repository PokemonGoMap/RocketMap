import os
import re
import time
import subprocess
import signal

compressRadius = "70"
compressTimeDiff = "120"

maxTries = 15
waittime = 1
base_dir = "spawns/"

compressedEnding = ".compressed.json"
for f in os.listdir( base_dir ):
    if f.endswith( compressedEnding ):
        continue
    
    fileName = base_dir + f
    newFileName = fileName[:-5] + compressedEnding
    
    arguments = [ "python", "Tools/Spawnpoint-Clustering/cluster.py", fileName, "-os", newFileName, "-r", compressRadius, "-t", compressTimeDiff ]
    
    if( os.path.isfile( newFileName ) ):
        print( "removing old file '%s'" % ( newFileName ) )
        os.remove( newFileName )
    
    app = subprocess.Popen( args=arguments )
    
    tryCount = 1
    lastFileSize = None
    while True:
        if( os.path.isfile( newFileName ) ):
            statinfo = os.stat( newFileName )
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
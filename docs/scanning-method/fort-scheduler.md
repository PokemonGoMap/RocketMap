# Fort Scheduler

Fort Scheduler is an alternative scheduler to Hex Scan meant primary for gym and raid scanning.

## Features

* Only scan locations where there are gyms and/or pokestops. 
* Optimize number of scans needed by clustering locations found
* Full support for geofencing of location
* No support for pokémon.

To use Fort Scheduler, put -fs in the command line or set `fort-scan` in your config file.

Fort Scheduler is only meant to be run after a database has been populated with gyms and/or stops with speed/hex scheduler.

**WARNING**: Take special note that the Fort Scheduler will trigger captchas if the accounts used are not leveled up to 2 before being used.  


## Commands and configs

What command line args should I use for scanning gyms only?

> Here's an example: `runserver.py -sch FortSearch -np -nk -sd 60 -w 10 -ac accounts.csv`

How big should I make my -st?

> Fort Scheduler does not care about your step size. It will scan whatever gyms/pokestops are in your db, filtered by your geofence if you suply one.

What should I set scan delay (-sd) to?

> Scan delay with Fort Scanner will determine how fast all gyms/stops will be scanned. If you have 6 gyms in your instance and want 1 worker to scan each gym/stop every minute, you can set `-sd 10` (1 location every 10 seconds for 6 locations = 60 seconds total).

## How many workers do I need ? 
There are three considerations. The number of gyms/stops, the number of workers you want to use, and how often you want to scan each location.

Because of clustering of gyms that are close together, the number of locations that will be searched will be lower. Run RM on your gym instance and look at the log how many locations there are after clustering

**Example**:
We have 200 gyms we want to scan:

 - 126 locations after clustering
 - We want the scanner to visit every gym once every minute
 - We don't want to put scan delay lower than 10, so that won't work on 1 worker.
 
 ` 60 seconds / 10 seconds` = 6 gyms per minute for one worker  
 
 ` 126 gyms / 6 gyms per minute per worker = ` 21 workers  

arguments: `runserver.py -sch FortSearch -np -nk -sd 10 -w 21`

If we allow each gym to only be scanned every 2nd minute, was can reduce the workers to 10

arguments: `runserver.py -sch FortSearch -np -nk -sd 10 -w 10`

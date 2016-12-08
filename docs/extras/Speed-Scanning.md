# Speed Scanning

## Features

Limit speed according to default of 35 kph or by setting -kph
Do an initial scan of the full area, then automatically switch to tracking down the exact spawn time (finding the TTH) and only scan for spawns (an -ss like behaviour).
Add spawn point type identification of the three current types of spawn points -- 15, 30, and 60 minute spawns.
Change spawn point scans to correct spawn time according to spawnpoint type
Add scans to complete identification for partially identified spawn points
Dynamically identify and check duration of new spawn points without requiring return to Hex scanning
Identify spawn points that have been removed and stop scanning them

To use Speed Scan, always put -speed in the command line.

## FAQ

> What command line args should I use for Speed Scan?

Here's an example: `runserver.py -speed -st 25 -w 100 -ac accounts.csv`

> Is there a different command line option to tell SpeedScan to do an initial scan or to do -ss (spawnpoint based scanning)?

SpeedScan workers are independent and look for the best scans they reach under the speed limit. The priority is initial scans, TTH, and then spawns. If a worker can not reach an initial scan under the speed limit, it will do a TTH search. If it can't do an initial scan or a TTH search, it will scan for new pokemon spawns, so all workers are always doing their best to find pokemon. Always put -speed in the command line.

> How does Speedscan find the time_til_hidden or TTH?

At the last minute or so of a Pokemon spawn, the servers include a time stamp of when the pokemon will disappear, called the time_til_hidden (TTH). Until the TTH is found, spawns are scanned twice -- once when they first spawn and again at the end of their spawn window to find the time_til_hidden and get the exact spawn time. Speed Scan searches for the TTH by doing a search between the last seen time and 15 minutes after. If the spawn isn't there at this time, it searches again between that last seen time and earliest unseen time. Next check is between those times again, and so on. This reduces the time where the TTH could be by about half every search, so it should find the TTH within five or so searches.

> SpeedScan has been running for days, but the TTH found is still about 99%. Why doesn't it find 100% of the TTH?

There appear to be some rare spawns that are not simple 15, 30, or 60 minute spawns. These spawns may have hidden times or not end with a TTH period. Also, as the possible window for where the TTH could be gets smaller, the time for a worker to scan that location also becomes smaller, so it takes longer to hit the window and find the TTH. In any case, even without the TTH, once the overall TTH complete percent is high, most spawns are scanned within a few minutes of spawning.

> Does Speed Scan still find new spawns even if TTH complete percent is less than 100%?

Yes. For the few spawns where the TTH still hasn't been found, there is usually only a few minutes when it could be, so Speed Scan still queues those new spawns, and is probably only late to scan them by a minute or two.

>How many workers will I need?

Here's a rough formula for how many workers:

Workers = Cells / 20
Cells = (((steps * (steps - 1)) * 3) + 1)

With -st 26, you will have 1951 cells and need about 98 workers.

To do the initial scan in an hour so, at -kph 35, it takes about half a minute to get to a the next location to scan, and you will want to be able to scan all 1951 cells in about 10 minutes, so the workers Cells / 20. If you reduce the -kph from 35 by half, increase the workers by double.

SpeedScan will work with less workers, although it will take longer than an hour for the initial scan. After the initial scan, the number of workers is dependent on the spawn density. More or less workers may be required than during the initial scan to cover all new spawns.

> What should I set scan delay (-sd) to?

With the default speed limit of 35 kph, scan delay isn't needed. It takes about 12 seconds to get to a neighboring location, which is sufficient delay. If you include an -sd lower than 12 seconds, it won't have an effect. If you use a -sd higher than 12, it will decrease the amount of scans your workers can do.

> Does this work with beehives?

Unless scanning a very large area (> -st 45?), SpeedScan does not require beehives. Each worker independently looks for the best scan it can do closest to it, so they work well together without fencing off workers into different hives.

> Can I run multiple instances with Speed Scan with one DB?

Yes. That works fine.

> Can the instances overlap?

Yes.

> How does it find the spawn points without having data from a Hex Scan?

Magic. This is covered in more detail in my initial [PR#1386](https://github.com/PokemonGoMap/PokemonGo-Map/pull/1386)

> What happens when it finds a new spawn point after the initial scan is done?

If a spawn point is noticed while scanning other spawnpoints, that scan location alone is reset and fully scanned to find the spawn point duration and exact spawn time.

> How does it handle spawn points disappearing?

After a spawn point is not seen as expected over five times in a row, it stops scheduling scans for that spawnpoint. The data remains in the DB.

> How does it handle web changes in the search location?

For changing the location of the searcher, this should work, but with lots of rescanning of the initial scan. Each time you change the location of the server, Speed Scan will restart its initial scan. Since SpeedScan records data about each search location, it is sensitive to changes in the location, and has to start over with the initial scan every time it is changed. This is true even if you move back to an already scanned location, but the loc is only slightly different.

> Is the speed limit also used when changing the scanner location?

Yes. Each worker remembers it's last scan location and time, so if the scanner is moved, it will take the workers  time to get to the new location.

## Print Screen, Status Page, and Log Messages

> I'm seeing a lot of "[ WARNING] Nothing on nearby_pokemons or wild. Speed violation?" in the log. What could cause this?

Common causes:
* Not using -speed as an argument.
* If the DB worker table has been recently deleted and the script restarted, such as with -cd (clear DB) option, the old position of the workers is forgotten, so they may violate the speed limit.
* There *aren't* any pokemon nearby. In areas over water or without pokemon spawns in 200m, these messages may be common. This is just a warning, and the data for that position is recorded normally.

> I'm seeing a lot of "[ WARNING] Bad scan. Parsing found 0/0/0 pokemons/pokestops/gyms"

Common causes:
* captchas
* IP bans
* running Pogo-map with --no-gyms (-ng) and --no-pokestops (-nk), because SpeedScan uses visible Gyms and Pokestops to determine if a scan is valid. Try adding gyms and stops back into your scan.

> I'm seeing a lot of "[ WARNING] hhhs kind spawnpoint 12341234123 has no pokemon 2 times in a row"

Possible causes:
* During initial scan, Speed Scan makes guesses for spawn duration. Should reduce after initial scan done.
* Spawnpoint is one of the extremely rare double spawnpoints, and was scanned during it's hidden period
* Spawnpoint has been removed by Niantic. Speed Scan will no longer queue for scans after missing five times 

What does this line mean? `SpeedScan Overseer: Scanning status: 27 total waiting, 0 initial bands, 0 TTH searches, and 27 new spawns`

Intial bands are the scans done to find the spawn points, TTH searches are looking for the time_til_hidden stamp to find the exact spawn time, and new spawn searches are scanning new spawns.

How about this line? `Initial scan: 100.00%, TTH found: 100.00%, Spawns reached: 100.00%, Spawns found: 100.00%, Good scans 99.59%`

Initial scan is the search for spawn points and scans each location in five bands within an hour, about 12 minutes apart. This should take a little over an hour to reach 100% with sufficient workers.

TTH found is the percentage of spawn points for which the exact spawn time is known. This could take up to a day to get over 90%.

Spawns reached is the percentage of spawns that are scanned before their timer runs out and they disappear. Will be low during the initial scan and possibly while still finding TTHs, but should reach 100% afterwards with sufficient workers.

Good scans is scans that aren't 0/0/0. Should be over 99% generally. If not, see above note about 0/0/0 warnings.

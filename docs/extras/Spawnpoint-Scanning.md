# Spawnpoint Scanning

If you already have a large number of known spawnpoints it may be worth looking into Spawnpoint Scanning

Spawnpoint Scanning consists of only scanning an area in which a spawn has recently happened, this saves a large number of requests and also detects all spawns soon after they appear instead of whenever the scan gets round to them again

Spawnpoint Scanning is particularly useful in areas where spawns are spread out

To run Spawnpoint Scanning, you will need a .json file containing the spawns to search. to use it simply use:

```
-ss if YOURFILE.json
```

where if YOURFILE is the file containing the spawns.

if YOURFILE.json does not exist, it will be created from the collected spawn data in the database, however if you want for it to only use some of the data in the database, you can use the flags:

```
-ne "LAT,LNG"
-sw "LAT,LNG"
```
to make a clipping rectangle to source the spawns from

when using the -ss flag you do not need to use the -l flag as the scan locations are entirely controlled by the contents of the .json file
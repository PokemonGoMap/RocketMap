# Hashing Keys

## What are hash keys for?
Hash keys allow your client program (in this case RocketMap) to access the latest API using the Bossland Hashing service. Accessing Niantic's servers without using a hash key is using an older API that is easier for Niantic to flag and ban. RocketMap does not support scanning wothout a hashing key.

## Where do I get a hash key?
[Check out this FAQ](https://talk.pogodev.org/d/55-api-hashing-service-f-a-q)

## How many RPMs will I use?
There is no perfect way to know. There are many variables that must be considered, including your step size, spawn spoints, encounters.

Please don't ask *"What if my step size is _x_, and I have encounters for _y_ Pokemon"*
We still don't know.  Get a key, turn on your map and see if it works.

If you are getting rate limited then either get more keys, or lower your calls (disabling/reducing encounters, disabling gym details, and decreasing step size are a few ways to reduce calls)

You can get a more detailed view of how many Hashing key calls are being used by enabling the status view `-ps` / `--print-status` and typing `h` followed by the enter key *OR* go to `<YourMapUrl>/status` and enter the password you defined. The status of each of your workers and hashing keys will be displayed and continually update. [More information about the status page](https://rocketmap.readthedocs.io/en/develop/extras/status-page.html)  

### Understanding the stats

`remaining` - This is how many requests can be made across instances using this hashing key in the current minute.
`maximum` - This is the most requests per minute that can be made using this hashing key. *Note:* Bosslandhas reported tracking is off, so you might get slightly more than this. 
`peak` - The most requests per minute that has occurred since the last time your database was dropped. (If using sqlite, this will since the last time you started that instance.)
`average` - The average requests made per minute.   
`expiration` - When this hashing ket is set to expire. 

## Where do I enter my hash key?
Use `-hk YourHashKeyHere` / `--hash-key YourHashKeyHere`.  
If you use a configuration file, add the line `hash-key: YourHashKeyHere` to that file.

## What if I have more than one hash key?
Specify `-hk YourHashKeyHere -hk YourSecondHashKeyHere ...`.  
If you use a configuration file, use `hash-key: [YourHashKeyHere, YourSecondHashKeyHere, ...]` in the file.

## If you have multiple keys, how does RM decide which one to use? 
RM will load balance the keys untill a key is full. For example, if you had a 150 key and 500 key both will be used equally untill the 150 is full then only the 500 key would be utilized. 

## What does HashingQuotaExceededException('429: Request limited, error: ',) mean?
Any variant of this means you've exceeded the Requests Per Minute that your key allows. Currently, this is not being tracked accurately by Bossland, therefore, you will get more hasinging requests than wht you are paying for. 

## How about [ WARNING] Exception while downloading map: HashingOfflineException('502 Server Error',)
Hashing server is temporarily unavailable (possibly offline).

## And this one? BadHashRequestException('400: Bad request, error: Unauthorized',)
Either your key is expired, or the hashing servers are having issues.

## This one? TempHashingBanException('Your IP was temporarily banned for sending too many requests with invalid keys',)
You are using invalid keys, or... you guessed it, the hashing servers are having issues.

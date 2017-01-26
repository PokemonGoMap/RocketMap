# Hash Keys

## What are hash keys for?
Up until API version 0.45 the pgoapi was able to directly access Niantic servers and make calls.
Because of the complex cat and mouse game played, Niantic upped the complexity with API 0.51.  The only way to access that API was through a hash key.
Legacy 0.45 could still be accessed.
on January 19th, 2017 Niantic did a force update of the Pokemon Go Client. This forced the actual clients to use API version 0.53.  This also requires a hash key.
At this writing legacy 0.45 is still available.

However, with a forced update Niantic can easily see clients authenticatin using 0.45. These accounts can/will be banned.

It is recommended to use hash keys to replicate authenticity of your client and reduce in-game captch costs.

## Where do I get a hash key?
[Check out this FAQ](https://talk.pogodev.org/d/55-api-hashing-service-f-a-q)

## How many RPMs will I use?
There is no perfect way to know. There are many variables that must be considered.  Including your step size, spawn spoints, encounters.

Please don't ask *"What if my step size is _x_, and I have encounters for _y_ Pokemon"*

We still don't know.  Get a key, turn on your map and see if it works.
If you are getting rate limited then either get more keys, or lower your calls (encounters, step size, etc)


## What does HashingQuotaExceededException('429: Request limited, error: ',) mean?
Any variant of this means you've exceeded the Requests Per Minute that your hashing key allows

## How about [ WARNING] Exception while downloading map: HashingOfflineException('502 Server Error',)
Hash server is most likely offline.

## And this one? BadHashRequestException('400: Bad request, error: Unauthorized',)
Either your key is expired, or the hashing servers are having issues.

## This one? TempHashingBanException('Your IP was temporarily banned for sending too many requests with invalid keys',)
You are using invalid keys, or... you guessed it, the hashing servers are having issues

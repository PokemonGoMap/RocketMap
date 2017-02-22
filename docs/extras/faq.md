# Common Questions and Answers

## Critical Error "Missing sprite files"

If you're unaware of what sprites are, the friendly users on our Discord are more than willing to explain. [RocketMap Discord](https://discord.gg/PWp2bAm).

## Can I sign in with Google?

Yes you can! Pass the flag `-a google` (replacing `-a ptc`) to use Google authentication.

If you happen to have 2-step verification enabled for your Google account you will need to supply an [app password](https://support.google.com/accounts/answer/185833?hl=en) for your password instead of your normal login password.

## Which is the best scan option to use to find pokemon?

Speed-Scheduler is the only scheduler that has been updated in recent times, it is also the most useful as it has many features such 
as finding exact spawnpoint times and duration and limiting speed to stop violations.
More information can be found here : [Speed Scheduler] (https://rocketmap.readthedocs.io/en/develop/extras/Speed-Scheduler.html)

## But I was happy using the default Hex or Spawnpoint scanning...

Speed- Scheduler combines both and is more efficient.

## Should I swap back to spawn point scanning after the speed-scheduler has done its initial scan?

No, It will automatically spawn scanpoints.

## All pokemon dissapear after only 1 minute, the map is broken!

One of Niantic's updates removed spawn timers from Pokémon (until there's little time left until they despawn). SpeedScan does an initial scan to determine all spawn points and their timers and automatically transitions into spawn scanning once it found them all. 
Seeing 1-minute timers during initial scan is perfectly normal.

## Whats the simplest command to start the map scanning?

./runserver.py -speed -l LOCATION -u USER -p PASS -k GOOGLEKEY
Please dont just paste that, replace location, user, pass and google map key

## Nice what other stuff can I use in the command line?

There is a list [here](https://rocketmap.readthedocs.io/en/develop/extras/commandline.html) or a more up to date list can be found by running ./runserver.py -h 

## Woah I added a ton of cool stuff and now my command line is massive

It is a lot simplier to use a [config file] (https://rocketmap.readthedocs.io/en/develop/extras/configuration-files.html)

## Can I scan for free or do I need to pay for a hash key?

You can use the the free api (0.45) but be aware that api is old and it is easy to be spotted and flagged for captcha or bans. Using a [hash key](https://hashing.pogodev.org/) uses the latest api and reduces captchas or removes them almost completely.

## Is there anything I can do to lower captchas on either api version?

Yes, you can level your workers to level two(spin a single pokéstop manually), this reduces captchas a lot. you may also consider scanning a smaller area, using less workers or encountering less pokemon for IV.

## example.py isn't working right

10/10 would run again


# Lets get technical

## I have problems with my database because......

RocketMap uses SQLite as default, this is really basic and not fit for realtime use. Please consider swapping to use something like [MySQL] (https://rocketmap.readthedocs.io/en/develop/extras/mysql.html)

## How do I setup port forwarding?

[See this helpful guide](external.md)

## I edited my files/installed unfinished code and messed up, will you help me fix it?

No, my advice is delete it all and start again, this time don't edit files unless you know what you are doing.

## I'm getting this error...

```
pip or python is not recognized as an internal or external command
```

[Python/pip has not been added to the environment](https://github.com/Langoor2/PokemonGo-Map-FAQ/blob/master/FAQ/Enviroment_Variables_not_correct.md) or [pip needs to be installed to retrieve all the dependencies](https://github.com/AHAAAAAAA/PokemonGo-Map/wiki/Installation-and-requirements)

```
Exception, e <- Invalid syntax.
```

This error is caused by Python 3. The project requires python 2.7

```
error: command 'gcc' failed with exit status 1

# - or -

[...]failed with error code 1 in /tmp/pip-build-k3oWzv/pycryptodomex/
```

Your OS is missing the `gcc` compiler library. For Debian, run `apt-get install build-essentials`. For Red Hat, run `yum groupinstall 'Development Tools'`

```
cells = map_dict['responses']['GET_MAP_OBJECTS']['map_cells']

KeyError: 'map_cells'
```

The account is banned or hasn't completed the tutorial.


## I have more questions!

Please read the [Wiki](https://rocketmap.readthedocs.io/en/develop/extras/configuration-files.html) for information and then join us on the [RocketMap Discord](https://discord.gg/PWp2bAm).


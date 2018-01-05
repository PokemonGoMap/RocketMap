# Account leveling
RocketMap completes the tutorial steps on all accounts on first log in and sets a pokemon as buddy if it does not have one.

Accounts with level 1 will get captchas after some time and will stop working unless you setup [catpcha handling](http://rocketmap.readthedocs.io/en/develop/first-run/captchas.html):


To avoid this it is recommended to level accounts at least to level 2, that is as simple as spin a pokestop and there are two ways to do so from RM:

 * Enabling pokestop spinning during regular operation
 * Using the levelup tool provided with RM

## Pokestop Spinning

To enable Pokéstop spinning, add pokestop-spinning to your configuration file, or -spin to your cli parameters.

```
pokestop-spinning
```

This setting will spin a pokestop as the account see one that is spinnable (inside the radius) if the account is still at level 1, otherwise if the `account-max-spins` limit is not reached (default is 20 per account per hour prorrated to the minute) the account has a 50% chance to spin it.

This setting could be enough for some maps with high density of stops, as the accounts will get near one soon enough to avoid the captcha, otherwise you will need to enable [catpcha handling](http://rocketmap.readthedocs.io/en/develop/first-run/captchas.html) to keep them working until there is a stop near.

## Levelup tool

Inside the RM folder there is a small python script that will go through the account list, ask for the map at 1 location, and spin all stops in range (following `account-max-spins` limit), that way you can be sure that accounts are properly leveled before using them.

The tool uses the same config file and options as RM (the ones that apply) so the setup and run is pretty simple, just change the location to some coodinates that are near 1 or more pokestops and change the worker setting to the number of simultaneus accounts you want to level up.

In the console you will see the initial level of each account, the spining and the final level, the script will end when all accounts have done the process or have failed 3 times.

To run it just make sure you are at RM root folder (it will not work otherwise) and just call:

```
python tools/levelup.py
```

All command line flags available in RM can be used here too (but not all will have any effect). So you could increase `account-max-spins` and change location and workers from the command line without needing to modify the config file with something like:

```
python tools/levelup.py -w 30 -l 40.417281,-3.683235 -ams 1000
```

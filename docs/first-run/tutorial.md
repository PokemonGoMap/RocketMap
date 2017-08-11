# Tutorial Completion
## RocketMap's tutorial completion for new accounts
RocketMap now completes the tutorial steps on all accounts on first log in, there is no more `-tut` argument to complete the tutorial.

It's recommended to enable pokestop spinning in the config to get your accounts to level 2.

For this, use -spin in commandline or set in the config file:

```
pokestop-spinning: true
```

You can also set the maximum number of Pokestop spins per hour, which by default is 80, and for example, lower it to 30, putting in the commandline -ams 30 or in the config file:

```
account-max-spins: 30
```

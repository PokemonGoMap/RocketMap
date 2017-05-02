# Webhooks

As of [#2019](https://github.com/AHAAAAAAA/PokemonGo-Map/pull/2019), webhooks have been implemented into RocketMap. Using these webhooks are simple, and opens up a new realm of possibilities for over almost anything related to RocketMap.

## How Do RocketMap Webhooks Work?

Every time an event occurs (e.g. a Pokemon spawns) a POST request will be sent to a provided URL containing information about that event. A developer may create a listener in whatever language they feel most comfortable in (it just has to handle incoming connections, after all) and do certain things when information from the webhook is received. For example, a developer would be able to wait for a Dragonite to spawn, then play a loud alarm throughout the house and flash the lights in order to get their attention. All of this could be done without even the slightest touch to the internal RocketMap code, so there's no risk to break anything.

## Types of Webhooks

Pokemon Spawn webhooks are available. More webhooks should be on the way! If you're a developer, feel free to contribute by creating some more webhooks.

| Name | Notes |
|---|---|
| `pokemon` | Emitted every time a Pokemon spawns.  |
| `gym` | Emitted when finding a gym. |
| `pokestop` | Emitted when finding a pokestop. |
| `pokestop_lured` | Emitted every time a Pokestop is lured. |
| `gym_defeated` |  Emitted every time a Gym is defeated (prestige changes) |
| `gym_conquered` |  Emitted every time the owner of a Gym is changed |

## PokeAlarm

PokeAlarm is an example of a script you can run to accept webhook data and send it elsewhere. In PokeAlarm's usage it is publishing that information on Facebook, Twitter, Discord, etc. 

[Learn More Here](https://github.com/kvangent/PokeAlarm)

## Configuring Webhooks
Add `-wh http://my-webhook/location` argument when starting RocketMap (runserver.py) to define the location of your webhook. You can add multiple webhook locations to a single -wh argument to define multiple webhooks.


```

To use this, RocketMap would be run with the following parameters:

```
python runserver.py -a ptc -u [username] -p [password] -l "Location or lat/lon" -st 15 -k [google maps api key] -wh http://localhost:9876
```


'use strict'

const Jimp = require('jimp')

const partsDir = 'static/icons/parts'
const gymsDir = 'static/icons/gyms'
const raidsDir = 'static/icons/raids'
const pokemonDir = 'static/icons/pokemon'

const teams = [
    'uncontested',
    'instinct',
    'mystic',
    'valor',
]

const teamColors = [
    '#FFFFFF',
    '#FFBE08',
    '#00AAFF',
    '#FF1A1A'
]

const raidLevelColors = [
    '#FC70B0',
    '#FC70B0',
    '#FF9E16',
    '#FF9E16',
    '#B8A5DD'
]

const raidBosses = {
    '1': [129, 153, 156, 159],
    '2': [89, 103, 110, 125, 126],
    '3': [59, 65, 68, 94, 134, 135, 136],
    '4': [3, 6, 9, 112, 131, 143, 248],
    '5': [144, 145, 146, 150, 243, 244, 245, 249, 250]
}

function collectIconResources() {
    const iconResources = [
        {
            name: 'circle',
            promise: Jimp.read(`${partsDir}/circle.png`),
            size: [68, 68]
        },
        {
            name: 'circle_border',
            promise: Jimp.read(`${partsDir}/circle_border.png`),
            size: [68, 68]
        }
    ]

    for (var i = 1; i <= 6; ++i) {
        iconResources.push({
            name: `number_${i}`,
            promise: Jimp.read(`${partsDir}/${i}.png`),
            size: [60, 60]
        })
    }

    for (var t = 0; t < teams.length; ++t) {
        iconResources.push({
            name: `gym_${teams[t]}`,
            promise: Jimp.read(`${partsDir}/gym_${teams[t]}.png`),
            size: [175, 175]
        })
    }

    for (var raidLevel = 1; raidLevel <= 5; ++raidLevel) {
        iconResources.push({
            name: `raid_egg_${raidLevel}`,
            promise: Jimp.read(`${partsDir}/raid_egg_${raidLevel}.png`),
            size: [110, 110]
        })

        for (var raidBoss in raidBosses[raidLevel]) {
            raidBoss = raidBosses[raidLevel][raidBoss]
            iconResources.push({
                name: `raid_boss_${raidBoss}`,
                promise: Jimp.read(`${pokemonDir}/${raidBoss}.png`),
                size: [145, 145]
            })
        }
    }

    return iconResources
}

function buildGymIcon(iconMap, teamId, numPokemon, raidLevel, raidBoss) {
    return new Promise(function(resolve, reject) {
        new Jimp(192, 192, function (err, icon) {
            if (err) {
                reject(err)
            }

            var team = teams[teamId]

            var circle = iconMap['circle']
            var circleBorder = iconMap['circle_border']

            var gym = iconMap[`gym_${team}`]
            icon = icon.composite(gym,
                                  (icon.bitmap.width / 2) - (gym.bitmap.width / 2),
                                  (icon.bitmap.height / 2) - (gym.bitmap.height / 2))

            // Raid egg
            var raidEgg = iconMap[`raid_egg_${raidLevel}`]
            if (raidLevel && raidLevel > 0 && !raidBoss) {
                icon = icon.composite(raidEgg,
                                      icon.bitmap.width - raidEgg.bitmap.width,
                                      icon.bitmap.height - raidEgg.bitmap.height - 5)
            }

            // Raid boss
            if (raidBoss) {
                var raidBossIcon = iconMap[`raid_boss_${raidBoss}`]
                icon = icon.composite(raidBossIcon,
                                      0,
                                      icon.bitmap.height - raidBossIcon.bitmap.height)
            }

            // Gym strength
            if (numPokemon && numPokemon > 0 && !raidBoss) {
                var numPokemonBkg = circle.clone()
                                          .color([{
                                               apply: 'mix',
                                               params: [teamColors[teamId], 100]
                                          }])
                                          .background(0x0)

                if (raidLevel && raidLevel > 0) {
                    var numPokemonX = (icon.bitmap.width / 2)
                                           - (numPokemonBkg.bitmap.width / 2)
                                           - 3
                } else {
                    var numPokemonX = (icon.bitmap.width / 2) - 12
                }

                var numPokemonY = icon.bitmap.height
                                      - (circleBorder.bitmap.height / 2)

                icon = icon.composite(numPokemonBkg,
                                      numPokemonX
                                          - (numPokemonBkg.bitmap.width / 2),
                                      numPokemonY
                                          - (numPokemonBkg.bitmap.height / 2))
                icon = icon.composite(circleBorder,
                                      numPokemonX
                                          - (circleBorder.bitmap.width / 2),
                                      numPokemonY
                                          - (circleBorder.bitmap.height / 2))
            }

            // Raid level
            if (raidLevel && raidLevel > 0) {
                var raidLevelBkg = circle.clone()
                                         .color([{
                                              apply: 'mix',
                                              params: [raidLevelColors[raidLevel - 1], 100]
                                         }])
                                         .background(0x0)
                var raidLevelNum = iconMap[`number_${raidLevel}`]
                var raidLevelHeight = icon.bitmap.height
                                          - (circleBorder.bitmap.height / 2)

                icon = icon.composite(raidLevelBkg,
                                      icon.bitmap.width
                                          - (raidEgg.bitmap.width / 2)
                                          - (raidLevelBkg.bitmap.width / 2),
                                      raidLevelHeight
                                          - (raidLevelBkg.bitmap.height / 2))
                icon = icon.composite(circleBorder,
                                      icon.bitmap.width
                                          - (raidEgg.bitmap.width / 2)
                                          - (circleBorder.bitmap.width / 2),
                                      raidLevelHeight
                                          - (circleBorder.bitmap.height / 2))
                icon = icon.composite(raidLevelNum,
                                      icon.bitmap.width
                                          - (raidEgg.bitmap.width / 2)
                                          - (raidLevelNum.bitmap.width / 2),
                                      raidLevelHeight
                                          - (raidLevelNum.bitmap.height / 2))
            }

            // Gym strength number
            if (numPokemon && numPokemon > 0 && !raidBoss) {
                var numPokemonNum = iconMap[`number_${numPokemon}`]
                icon = icon.composite(numPokemonNum,
                                      numPokemonX
                                          - (numPokemonNum.bitmap.width / 2),
                                      numPokemonY
                                          - (numPokemonNum.bitmap.height / 2))
            }

            var name = `${team}_${numPokemon || 0}_${raidLevel || 0}`
            if (raidBoss) {
                name += `_${raidBoss}`
            }

            icon.write(`${gymsDir}/${name}.png`, function() {
                resolve()
            })
        })
    })
}

module.exports = function() {
    const iconPromisesMap = collectIconResources()

    const iconPromises = iconPromisesMap.map(function (icon) {
        return icon.promise
    })

    return new Promise(function (resolve, reject) {
        Promise.all(iconPromises)
        .then(function (icons) {
            const iconMap = {}

            icons.forEach(function (icon, index) {
                var size = iconPromisesMap[index].size
                if (size) {
                    icon.resize(size[0], size[1])
                        .background(0x0)
                }
                iconMap[iconPromisesMap[index].name] = icon
            })

            const generationPromises = []

            // All gyms
            for (var teamId = 0; teamId < teams.length; ++teamId) {
                for (var raidLevel = 0; raidLevel <= 5; ++raidLevel) {
                    // Gym icons with just raid eggs (no pokemon or raid bosses)
                    generationPromises.push(
                        buildGymIcon(iconMap, teamId, 0, raidLevel))
                
                    // Gym icons with just raid bosses (and no pokemon)
                    if (raidLevel > 0) {
                        for (var raidBoss in raidBosses[raidLevel]) {
                            raidBoss = raidBosses[raidLevel][raidBoss]
                            generationPromises.push(
                                buildGymIcon(iconMap, teamId, 0, raidLevel, raidBoss))
                        }
                    }
                }
            }

            // Only contested gyms
            for (var teamId = 1; teamId < teams.length; ++teamId) {
                // Plain gym icon (no pokemon, raid eggs or raid bosses)
                generationPromises.push(buildGymIcon(iconMap, teamId))

                // Gym icons with pokemon and raid eggs (but no raid bosses)
                for (var numPokemon = 0; numPokemon <= 6; ++numPokemon) {
                    for (var raidLevel = 0; raidLevel <= 5; ++raidLevel) {
                        generationPromises.push(
                            buildGymIcon(iconMap, teamId, numPokemon, raidLevel))
                    }
                }
            }
            
            Promise.all(generationPromises)
            .then(function() {
                resolve()
            })
        }).catch(function (err) {
            reject(err)
        })
    })
}

'use strict'

const fs = require('fs')
const Jimp = require('jimp')

const iconsDir = 'static/icons'
const partsDir = `${iconsDir}/parts`
const gymsDir = `${iconsDir}/gyms`
const pokemonDir = `${iconsDir}/pokemon`

const teams = [
    'uncontested',
    'instinct',
    'mystic',
    'valor'
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
    '1': [2, 5, 8, 11],
    /* Ivysaur, Charmeleon, Wartortle, Metapod */
    '2': [28, 73, 82, 91, 105, 302],
    /* Sandslash, Tentacruel, Magneton, Cloyster, Marowak, Sableye */
    '3': [38, 65, 68, 94, 123, 137, 139],
    /* Ninetales, Alakazam, Machamp, Gengar, Scyther, Porygon, Omastar */
    '4': [31, 34, 62, 71, 76, 131, 143, 248],
    /* Nidoqueen, Nidoking, Poliwrath, Victreebel, Golem, Lapras, Snorlax, Tyranitar */
    '5': [144, 145, 146, 150, 243, 244, 245, 249, 250]
    /* Articuno, Zapdos, Moltres, Mewtwo, Raikou, Entei, Suicune, Lugia, Ho-Oh */
}

function iconAlreadyExists(name, type) {
    return fs.existsSync(`${iconsDir}/${type}/${name}.png`)
}

function collectBaseIconResources() {
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
        },
        {
            name: 'circle_large',
            promise: Jimp.read(`${partsDir}/circle.png`),
            size: [135, 135]
        }
    ]

    for (var i = 1; i <= 6; ++i) {
        iconResources.push({
            name: `number_${i}`,
            promise: Jimp.read(`${partsDir}/${i}.png`),
            size: [60, 60]
        })
    }

    return iconResources
}

function collectGymIconResources() {
    const iconResources = []

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
                size: [135, 135]
            })
        }
    }

    iconResources.push({
        name: 'raid_boss_unknown',
        promise: Jimp.read(`${partsDir}/id.png`),
        size: [135, 135]
    })

    return iconResources
}

function gymIconName(teamId, numPokemon, raidLevel, raidBoss) {
    var name = `${teams[teamId]}_${numPokemon || 0}_${raidLevel || 0}`

    if (raidBoss) {
        name += `_${raidBoss}`
    }

    return name
}

function buildGymIcon(iconMap, teamId, numPokemon, raidLevel, raidBoss) {
    return new Promise(function (resolve, reject) {
        // eslint-disable-next-line no-new
        new Jimp(192, 192, function (err, icon) {
            if (err) {
                reject(err)
            }

            const team = teams[teamId]

            const circle = iconMap['circle']
            const circleBorder = iconMap['circle_border']
            const largeCircle = iconMap['circle_large']

            const gym = iconMap[`gym_${team}`]
            icon = icon.composite(gym,
                                  (icon.bitmap.width / 2) - (gym.bitmap.width / 2),
                                  (icon.bitmap.height / 2) - (gym.bitmap.height / 2))

            // Raid egg
            const raidEgg = iconMap[`raid_egg_${raidLevel}`]
            if (raidLevel && raidLevel > 0 && !raidBoss) {
                icon = icon.composite(raidEgg,
                                      icon.bitmap.width - raidEgg.bitmap.width,
                                      icon.bitmap.height - raidEgg.bitmap.height - 5)
            }

            // Raid boss
            if (raidBoss) {
                const raidBossIcon = iconMap[`raid_boss_${raidBoss}`]

                if (raidBoss === 'unknown') {
                    const raidBossBkg = largeCircle.clone()
                                                   .color([{
                                                       apply: 'mix',
                                                       params: ['#CFCFCF', 100]
                                                   }])
                                                   .background(0x0)

                    icon = icon.composite(raidBossBkg,
                                          0, icon.bitmap.height - raidBossIcon.bitmap.height)
                }

                icon = icon.composite(raidBossIcon,
                                      0, icon.bitmap.height - raidBossIcon.bitmap.height)
            }

            // Gym strength
            const numPokemonY = icon.bitmap.height - (circleBorder.bitmap.height / 2)

            if (numPokemon && numPokemon > 0 && !raidBoss) {
                const numPokemonBkg = circle.clone()
                                            .color([{
                                                apply: 'mix',
                                                params: [teamColors[teamId], 100]
                                            }])
                                            .background(0x0)

                var numPokemonX
                if (raidLevel && raidLevel > 0) {
                    numPokemonX = (icon.bitmap.width / 2) -
                                  (numPokemonBkg.bitmap.width / 2) -
                                  3
                } else {
                    numPokemonX = (icon.bitmap.width / 2)
                }

                icon = icon.composite(numPokemonBkg,
                                      numPokemonX - (numPokemonBkg.bitmap.width / 2),
                                      numPokemonY - (numPokemonBkg.bitmap.height / 2))
                icon = icon.composite(circleBorder,
                                      numPokemonX - (circleBorder.bitmap.width / 2),
                                      numPokemonY - (circleBorder.bitmap.height / 2))
            }

            // Raid level
            if (raidLevel && raidLevel > 0) {
                const raidLevelBkg = circle.clone()
                                           .color([{
                                               apply: 'mix',
                                               params: [raidLevelColors[raidLevel - 1], 100]
                                           }])
                                           .background(0x0)
                const raidLevelNum = iconMap[`number_${raidLevel}`]
                const raidLevelHeight = icon.bitmap.height - (circleBorder.bitmap.height / 2)

                icon = icon.composite(raidLevelBkg,
                                      icon.bitmap.width -
                                      (raidEgg.bitmap.width / 2) -
                                      (raidLevelBkg.bitmap.width / 2),
                                      raidLevelHeight -
                                      (raidLevelBkg.bitmap.height / 2))
                icon = icon.composite(circleBorder,
                                      icon.bitmap.width -
                                      (raidEgg.bitmap.width / 2) -
                                      (circleBorder.bitmap.width / 2),
                                      raidLevelHeight -
                                      (circleBorder.bitmap.height / 2))
                icon = icon.composite(raidLevelNum,
                                      icon.bitmap.width -
                                      (raidEgg.bitmap.width / 2) -
                                      (raidLevelNum.bitmap.width / 2),
                                      raidLevelHeight -
                                      (raidLevelNum.bitmap.height / 2))
            }

            // Gym strength number
            if (numPokemon && numPokemon > 0 && !raidBoss) {
                const numPokemonNum = iconMap[`number_${numPokemon}`]
                icon = icon.composite(numPokemonNum,
                                      numPokemonX - (numPokemonNum.bitmap.width / 2),
                                      numPokemonY - (numPokemonNum.bitmap.height / 2))
            }

            const name = gymIconName(teamId, numPokemon, raidLevel, raidBoss)
            icon.write(`${gymsDir}/${name}.png`, function () {
                resolve(name)
            })
        })
    })
}

module.exports = function () {
    const iconPromisesMap = collectBaseIconResources().concat(collectGymIconResources())

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

            var iconName
            var teamId
            var raidLevel
            var rebuild = false

            // All gyms
            for (teamId = 0; teamId < teams.length; ++teamId) {
                for (raidLevel = 0; raidLevel <= 5; ++raidLevel) {
                    // Gym icons with just raid eggs (no pokemon or raid bosses)
                    iconName = gymIconName(teamId, 0, raidLevel)
                    if (!iconAlreadyExists(iconName, 'gyms') || rebuild) {
                        generationPromises.push(
                            buildGymIcon(iconMap, teamId, 0, raidLevel))
                    }

                    // Gym icons with just raid bosses (and no pokemon)
                    if (raidLevel > 0) {
                        for (var raidBoss in raidBosses[raidLevel]) {
                            raidBoss = raidBosses[raidLevel][raidBoss]
                            iconName = gymIconName(teamId, 0, raidLevel, raidBoss)
                            if (!iconAlreadyExists(iconName, 'gyms') || rebuild) {
                                generationPromises.push(
                                    buildGymIcon(iconMap, teamId, 0, raidLevel, raidBoss))
                            }
                        }

                        iconName = gymIconName(teamId, 0, raidLevel, 'unknown')
                        if (!iconAlreadyExists(iconName, 'gyms') || rebuild) {
                            generationPromises.push(
                                buildGymIcon(iconMap, teamId, 0, raidLevel, 'unknown'))
                        }
                    }
                }
            }

            // Only contested gyms
            for (teamId = 1; teamId < teams.length; ++teamId) {
                // Plain gym icon (no pokemon, raid eggs or raid bosses)
                iconName = gymIconName(teamId)
                if (!iconAlreadyExists(iconName, 'gyms') || rebuild) {
                    generationPromises.push(buildGymIcon(iconMap, teamId))
                }

                // Gym icons with pokemon and raid eggs (but no raid bosses)
                for (var numPokemon = 0; numPokemon <= 6; ++numPokemon) {
                    for (raidLevel = 0; raidLevel <= 5; ++raidLevel) {
                        iconName = gymIconName(teamId, numPokemon, raidLevel)
                        if (!iconAlreadyExists(iconName, 'gyms') || rebuild) {
                            generationPromises.push(
                                buildGymIcon(iconMap, teamId, numPokemon, raidLevel))
                        }
                    }
                }
            }

            Promise.all(generationPromises)
            .then(function (results) {
                console.log('>>'['green'] + ` ${results.length} icons built.`)
                resolve()
            })
        }).catch(function (err) {
            reject(err)
        })
    })
}

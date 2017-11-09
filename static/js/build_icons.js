'use strict'

const fs = require('fs')
const Jimp = require('jimp')

const iconsDir = 'static/icons'
const partsDir = `${iconsDir}/parts`
const pokemonDir = `${iconsDir}/pokemon`
const gymsDir = `${iconsDir}/gyms`
const fontsDir = 'static/fonts'

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

const rebuild = true

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

function textWidth(font, text) {
    var width = 0

    for (let c = 0; c < text.length; ++c) {
        if (font.kernings[text[c]] && font.kernings[text[c]][text[c + 1]]) {
            width += font.kernings[text[c]][text[c + 1]]
        }

        width += font.chars[text[c]].xadvance || 0
    }

    return width
}

function textHeight(font, text) {
    const heights = []

    for (var c = 0; c < text.length; ++c) {
        return font.chars[text[c]].height + (font.chars[text[c]].yoffset || 0)
    }

    return Math.max(heights)
}

function iconAlreadyExists(name, type) {
    return fs.existsSync(`${iconsDir}/${type}/${name}.png`)
}

function loadPokemonData() {
    const pokemonDataStr = fs.readFileSync('static/data/pokemon.json', 'utf8')
    return JSON.parse(pokemonDataStr)
}

function loadPokemonForms() {
    const pokemonFormsStr = fs.readFileSync('static/data/pokemon_forms.json', 'utf8')
    return JSON.parse(pokemonFormsStr).pokemon_forms
}

function pokemonIconName(pokemon, form) {
    return pokemon.id + (form ? `-${form.name}` : '')
}

function gymIconName(teamId, numPokemon, raidLevel, raidBoss) {
    return `${teams[teamId]}_${numPokemon || 0}_${raidLevel || 0}` +
           (raidBoss ? `_${raidBoss}` : '')
}

function parseForm(form) {
    if (Array.isArray(form)) {
        return {
            symbol: form[0],
            name: form[1]
        }
    }

    return {
        symbol: form,
        name: form.toLowerCase()
    }
}

function loadIconResource(name, path, size) {
    return Promise.all([
        'icon',
        name,
        Jimp.read(path),
        size
    ])
}

function loadFontResource(name, path) {
    return Promise.all([
        'icon',
        name,
        Jimp.loadFont(path)
    ])
}

function collectPokemonResources() {
    return [
        loadIconResource('circle',
                         `${partsDir}/circle.png`,
                         [192, 192]),
        loadIconResource('rect',
                         `${partsDir}/rect.png`,
                         [192, 192]),
        loadFontResource('font_open_sans_bold_72_white',
                         `${fontsDir}/open-sans-bold-72-white.fnt`),
        loadFontResource('font_open_sans_bold_60_white',
                         `${fontsDir}/open-sans-bold-60-white.fnt`)
    ]
}

function collectGymResources() {
    const resources = [
        loadIconResource('circle_small',
                         `${partsDir}/circle.png`,
                         [68, 68]),
        loadIconResource('circle_medium',
                         `${partsDir}/circle.png`,
                         [135, 135]),
        loadIconResource('circle_border_small',
                         `${partsDir}/circle_border.png`,
                         [68, 68]),
        loadIconResource('raid_boss_unknown',
                         `${partsDir}/id.png`,
                         [135, 135])
    ]

    for (var i = 1; i <= 6; ++i) {
        resources.push(
            loadIconResource(`gym_strength_${i}`,
                             `${partsDir}/${i}.png`,
                             [60, 60]))

        resources.push(
            loadIconResource(`raid_level_${i}`,
                             `${partsDir}/${i}.png`,
                             [50, 50]))
    }

    for (var t = 0; t < teams.length; ++t) {
        resources.push(
            loadIconResource(`gym_${teams[t]}`,
                             `${partsDir}/gym_${teams[t]}.png`,
                             [170, 170]))
    }

    for (var raidLevel = 1; raidLevel <= 5; ++raidLevel) {
        resources.push(
            loadIconResource(`raid_egg_${raidLevel}`,
                             `${partsDir}/raid_egg_${raidLevel}.png`,
                             [110, 110]))

        resources.push(
            loadIconResource(`raid_star_${raidLevel}`,
                             `${partsDir}/raid_star_${raidLevel}.png`,
                             [80, 80]))

        for (var raidBoss in raidBosses[raidLevel]) {
            raidBoss = raidBosses[raidLevel][raidBoss]
            resources.push(
                loadIconResource(`raid_boss_${raidBoss}`,
                                 `${pokemonDir}/${raidBoss}.png`,
                                 [135, 135]))
        }
    }

    return resources
}

function buildResourceMap(resources) {
    const resourceMap = {}

    resources.forEach(function (resource) {
        const type = resource[0]
        const name = resource[1]

        switch (type) {
            case 'icon':
                const icon = resource[2]
                const size = resource[3]
                
                if (size && (icon.bitmap.width != size[0] || icon.bitmap.height != size[1])) {
                    resourceMap[name] = icon.resize(size[0], size[1])
                                            .background(0x0)
                } else {
                    resourceMap[name] = icon
                }

                break

            case 'font':
                const font = resource[2]
                resourceMap[name] = font
                break
        }
    })

    return resourceMap
}

function buildPokemonIcon(resourceMap, pokemon, form) {
    return new Promise(function (resolve, reject) {
        // eslint-disable-next-line no-new
        new Jimp(192, 192, function (err, icon) {
            if (err) {
                reject(err)
            }

            const circle = resourceMap['circle']
            const rect = resourceMap['rect']
            const largeFont = resourceMap['font_open_sans_bold_72_white']
            const smallFont = resourceMap['font_open_sans_bold_60_white']

            // Background circle
            const pokemonBkg = circle.clone()
                                     .color([{
                                         apply: 'mix',
                                         params: [pokemon.types[0].color, 100]
                                     }])
                                     .background(0x0)

            icon = icon.composite(pokemonBkg,
                                  (icon.bitmap.width / 2) - (pokemonBkg.bitmap.width / 2),
                                  (icon.bitmap.height / 2) - (pokemonBkg.bitmap.height / 2))

            // Text
            const idText = pokemon.id.toString()

            if (form) {
                // ID and form
                const formText = form.symbol
                icon.print(smallFont,
                           (pokemonBkg.bitmap.width / 2) -
                           (textWidth(smallFont, idText) / 2),
                           (pokemonBkg.bitmap.height / 2) -
                           textHeight(smallFont, idText)
                           - 7,
                           idText)
                icon.print(smallFont,
                           (pokemonBkg.bitmap.width / 2) -
                           (textWidth(smallFont, formText) / 2),
                           (pokemonBkg.bitmap.height / 2)
                           + 7,
                           formText)
            } else {
                // Just ID
                icon.print(largeFont,
                           (pokemonBkg.bitmap.width / 2) -
                           (textWidth(largeFont, idText) / 2),
                           (pokemonBkg.bitmap.height / 2) -
                           (textHeight(largeFont, idText) / 2),
                           idText)
            }

            const name = pokemonIconName(pokemon, form)
            icon.write(`${pokemonDir}/${name}.png`, function () {
                resolve(name)
            })
        })
    })
}

function buildGymIcon(resourceMap, teamId, numPokemon, raidLevel, raidBoss) {
    return new Promise(function (resolve, reject) {
        // eslint-disable-next-line no-new
        new Jimp(192, 192, function (err, icon) {
            if (err) {
                reject(err)
            }

            const team = teams[teamId]

            const circle = resourceMap['circle_small']
            const circleBorder = resourceMap['circle_border_small']
            const largerCircle = resourceMap['circle_medium']

            const gym = resourceMap[`gym_${team}`]
            icon = icon.composite(gym,
                                  (icon.bitmap.width / 2) - (gym.bitmap.width / 2),
                                  (icon.bitmap.height / 2) - (gym.bitmap.height / 2))

            // Raid egg
            const raidEgg = resourceMap[`raid_egg_${raidLevel}`]
            if (raidLevel && raidLevel > 0 && !raidBoss) {
                icon = icon.composite(raidEgg,
                                      icon.bitmap.width - raidEgg.bitmap.width,
                                      icon.bitmap.height - raidEgg.bitmap.height - 12)
            }

            // Raid boss
            if (raidBoss) {
                const raidBossIcon = resourceMap[`raid_boss_${raidBoss}`]

                if (raidBoss === 'unknown') {
                    const raidBossBkg = largerCircle.clone()
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
                    numPokemonX = (icon.bitmap.width / 2) - 12
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
                const raidLevelBkg = resourceMap[`raid_star_${raidLevel}`].clone()
                const raidLevelNum = resourceMap[`raid_level_${raidLevel}`]
                const raidLevelHeight = icon.bitmap.height - (raidLevelBkg.bitmap.height / 2)

                icon = icon.composite(raidLevelBkg,
                                      icon.bitmap.width -
                                      (raidEgg.bitmap.width / 2) -
                                      (raidLevelBkg.bitmap.width / 2),
                                      raidLevelHeight -
                                      (raidLevelBkg.bitmap.height / 2))
                icon = icon.composite(raidLevelNum,
                                      icon.bitmap.width -
                                      (raidEgg.bitmap.width / 2) -
                                      (raidLevelNum.bitmap.width / 2),
                                      raidLevelHeight -
                                      (raidLevelNum.bitmap.height / 2) +
                                      5)
            }

            // Gym strength number
            if (numPokemon && numPokemon > 0 && !raidBoss) {
                const numPokemonNum = resourceMap[`gym_strength_${numPokemon}`]
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
    const pokemonResourcePromises = collectPokemonResources()

    return Promise.all(pokemonResourcePromises)
    .then(function (resources) {
        const resourceMap = buildResourceMap(resources)
        const pokemonData = loadPokemonData()
        const pokemonForms = loadPokemonForms()
        const pokemonIconPromises = []

        var iconName

        for (var pokemonId = 1; pokemonId <= 386; ++pokemonId) {
            var pokemon = pokemonData[pokemonId]
            pokemon.id = pokemonId

            // Base icon
            iconName = pokemonIconName(pokemon)
            if (!iconAlreadyExists(iconName, 'pokemon') || rebuild) {
                pokemonIconPromises.push(
                    buildPokemonIcon(resourceMap, pokemon))
            }

            // Form icons
            var formData = pokemonForms.find(function (pokemonForm) {
                return pokemonForm.pokemon == pokemon.id
            })
            if (formData) {
                formData.forms.forEach(function (form) {
                    form = parseForm(form)
                    iconName = pokemonIconName(pokemon, form)
                    if (!iconAlreadyExists(iconName, 'pokemon') || rebuild) {
                        pokemonIconPromises.push(
                            buildPokemonIcon(resourceMap, pokemon, form))
                    }
                })
            }
        }

        return Promise.all(pokemonIconPromises)
    })
    .then(function (results) {
        console.log('>>'['green'] + ` ${results.length} pokemon icons built.`)
    })
    .then(function () {
        const gymResourcePromises = collectGymResources()
        return Promise.all(gymResourcePromises)
    })
    .then(function (resources) {
        const resourceMap = buildResourceMap(resources)
        const gymIconPromises = []

        var iconName
        var teamId
        var raidLevel

        // All gyms
        for (teamId = 0; teamId < teams.length; ++teamId) {
            for (raidLevel = 0; raidLevel <= 5; ++raidLevel) {
                // Gym icons with just raid eggs (no pokemon or raid bosses)
                iconName = gymIconName(teamId, 0, raidLevel)
                if (!iconAlreadyExists(iconName, 'gyms') || rebuild) {
                    gymIconPromises.push(
                        buildGymIcon(resourceMap, teamId, 0, raidLevel))
                }

                // Gym icons with just raid bosses (and no pokemon)
                if (raidLevel > 0) {
                    for (var raidBoss in raidBosses[raidLevel]) {
                        raidBoss = raidBosses[raidLevel][raidBoss]
                        iconName = gymIconName(teamId, 0, raidLevel, raidBoss)
                        if (!iconAlreadyExists(iconName, 'gyms') || rebuild) {
                            gymIconPromises.push(
                                buildGymIcon(resourceMap, teamId, 0, raidLevel, raidBoss))
                        }
                    }

                    iconName = gymIconName(teamId, 0, raidLevel, 'unknown')
                    if (!iconAlreadyExists(iconName, 'gyms') || rebuild) {
                        gymIconPromises.push(
                            buildGymIcon(resourceMap, teamId, 0, raidLevel, 'unknown'))
                    }
                }
            }
        }

        // Only contested gyms
        for (teamId = 1; teamId < teams.length; ++teamId) {
            // Plain gym icon (no pokemon, raid eggs or raid bosses)
            iconName = gymIconName(teamId)
            if (!iconAlreadyExists(iconName, 'gyms') || rebuild) {
                gymIconPromises.push(buildGymIcon(resourceMap, teamId))
            }

            // Gym icons with pokemon and raid eggs (but no raid bosses)
            for (var numPokemon = 0; numPokemon <= 6; ++numPokemon) {
                for (raidLevel = 0; raidLevel <= 5; ++raidLevel) {
                    iconName = gymIconName(teamId, numPokemon, raidLevel)
                    if (!iconAlreadyExists(iconName, 'gyms') || rebuild) {
                        gymIconPromises.push(
                            buildGymIcon(resourceMap, teamId, numPokemon, raidLevel))
                    }
                }
            }
        }

        return Promise.all(gymIconPromises)
    })
    .then(function (results) {
        console.log('>>'['green'] + ` ${results.length} gym icons built.`)
    })
    .catch(function (err) {
        console.log('>> '['red'] + (err.stack || err))
        throw err
    })
}

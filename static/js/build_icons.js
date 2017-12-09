'use strict'

const fs = require('fs')
const readline = require('readline')
const FileChanged = require('file-changed')
const Promise = require('bluebird')
const Jimp = require('jimp')

const iconsDir = 'static/icons'
const partsDir = `${iconsDir}/parts`
const pokemonDir = `${iconsDir}/pokemon`
const gymsDir = `${iconsDir}/gyms`
const fontsDir = 'static/fonts'

const resourceInfoPath = `${iconsDir}/.tracking`
const resourceInfo = new FileChanged(resourceInfoPath)

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

const unknownRaidBoss = 'unknown'
const unknownRaidBossText = '?'

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

const batchSize = 50

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

function iconAlreadyExists(type, name) {
    return fs.existsSync(`${iconsDir}/${type}/${name}.png`)
}

function pokemonIconName(pokemon, form) {
    return pokemon.id + (form ? `-${form.name}` : '')
}

function gymIconName(teamId, gymStrength, raidLevel, raidBoss) {
    return `${teams[teamId]}_${gymStrength || 0}_${raidLevel || 0}` +
           (raidBoss ? `_${raidBoss}` : '')
}

function parseForm(form) {
    if (Array.isArray(form)) {
        return {
            name: form[0],
            symbol: form[1]
        }
    }

    return {
        name: form,
        symbol: form.toUpperCase()
    }
}

function saveResourceInfo() {
    resourceInfo.addFile(`${iconsDir}/**/*.*`)
    resourceInfo.addFile(`${fontsDir}/**/*.*`)
    resourceInfo.clean()
    resourceInfo.update()
    resourceInfo.save()
}

function resourcePromise(resourceDetails) {
    const resource = [
        resourceDetails.type,
        resourceDetails.path,
        resourceDetails.name
    ]

    switch (resourceDetails.type) {
        case 'icon':
            resource.push(Jimp.read(resourceDetails.path))
            resource.push(resourceDetails.size)
            break

        case 'font':
            resource.push(Jimp.loadFont(resourceDetails.path))
            break
    }

    return Promise.all(resource)
}

function pokemonResourceDetails(pokemon, form) {
    const resourceDetails = [
        {
            type: 'icon',
            name: 'circle',
            path: `${partsDir}/circle.png`,
            size: [192, 192]
        }
    ]

    if (form) {
        resourceDetails.push({
            type: 'font',
            name: 'font',
            path: `${fontsDir}/open-sans-bold-60-white.fnt`
        })
    } else {
        resourceDetails.push({
            type: 'font',
            name: 'font',
            path: `${fontsDir}/open-sans-bold-72-white.fnt`
        })
    }

    return resourceDetails
}

function gymResourceDetails(teamId, gymStrength, raidLevel, raidBoss) {
    const resourceDetails = [
        {
            type: 'icon',
            name: 'small_circle',
            path: `${partsDir}/circle.png`,
            size: [68, 68]
        },
        {
            type: 'icon',
            name: 'large_circle',
            path: `${partsDir}/circle.png`,
            size: [150, 150]
        },
        {
            type: 'icon',
            name: 'circle_border',
            path: `${partsDir}/circle_border.png`,
            size: [68, 68]
        },
        {
            type: 'icon',
            name: 'gym',
            path: `${partsDir}/gym_${teams[teamId]}.png`,
            size: [170, 170]
        }
    ]

    if (gymStrength && gymStrength > 0) {
        resourceDetails.push({
            type: 'icon',
            name: 'gym_strength',
            path: `${partsDir}/${gymStrength}.png`,
            size: [60, 60]
        })
    }

    if (raidLevel && raidLevel > 0) {
        resourceDetails.push({
            type: 'icon',
            name: 'raid_level',
            path: `${partsDir}/${raidLevel}.png`,
            size: [50, 50]
        })

        resourceDetails.push({
            type: 'icon',
            name: 'raid_egg',
            path: `${partsDir}/raid_egg_${raidLevel}.png`,
            size: [105, 105]
        })

        resourceDetails.push({
            type: 'icon',
            name: 'raid_star',
            path: `${partsDir}/raid_star_${raidLevel}.png`,
            size: [80, 80]
        })
    }

    if (raidBoss) {
        if (raidBoss === 'unknown') {
            resourceDetails.push({
                type: 'font',
                name: 'font',
                path: `${fontsDir}/open-sans-bold-72-white.fnt`
            })
        } else {
            resourceDetails.push({
                type: 'icon',
                name: 'raid_boss',
                path: `${pokemonDir}/${raidBoss}.png`,
                size: [150, 150]
            })
        }
    }

    return resourceDetails
}

function resourceChanged(resourceDetails) {
    const changedResources = []
    resourceDetails.forEach(function (details) {
        if (fs.existsSync(details.path)) {
            changedResources.push(...resourceInfo.check(details.path))
        } else {
            changedResources.push(details.path)
        }
    })
    return changedResources.length > 0
}

function resourceDetailsHash(resourceDetails) {
    return resourceDetails.path +
           (resourceDetails.size ? `-${resourceDetails.size}` : '')
}

function getPokemonIconDetails() {
    const pokemonData = JSON.parse(
        fs.readFileSync('static/data/pokemon.json', 'utf8'))
    const pokemonForms = JSON.parse(
        fs.readFileSync('static/data/pokemon_forms.json', 'utf8'))
    const details = []

    for (var pokemonId = 1; pokemonId <= 386; ++pokemonId) {
        const pokemon = pokemonData[pokemonId]
        const forms = pokemonForms[pokemonId]

        pokemon.id = pokemonId

        if (forms) {
            forms.forEach(function (form) {
                form = parseForm(form)
                details.push({
                    name: pokemonIconName(pokemon, form),
                    pokemon: pokemon,
                    form: form,
                    resourceDetails: pokemonResourceDetails(pokemon, form)
                })
            })
        } else {
            details.push({
                name: pokemonIconName(pokemon),
                pokemon: pokemon,
                resourceDetails: pokemonResourceDetails(pokemon)
            })
        }
    }

    return details
}

function getGymIconDetails() {
    const details = []

    var teamId
    var raidLevel

    // All gyms
    for (teamId = 0; teamId < teams.length; ++teamId) {
        for (raidLevel = 0; raidLevel <= 5; ++raidLevel) {
            // Gym icons with just raid eggs
            details.push({
                name: gymIconName(teamId, 0, raidLevel),
                teamId: teamId,
                gymStrength: 0,
                raidLevel: raidLevel,
                resourceDetails: gymResourceDetails(teamId, 0, raidLevel)
            })

            // Gym icons with just raid bosses
            if (raidLevel > 0) {
                for (var raidBoss in raidBosses[raidLevel]) {
                    raidBoss = raidBosses[raidLevel][raidBoss]
                    details.push({
                        name: gymIconName(teamId, 0, raidLevel, raidBoss),
                        teamId: teamId,
                        gymStrength: 0,
                        raidLevel: raidLevel,
                        raidBoss: raidBoss,
                        resourceDetails: gymResourceDetails(teamId, 0, raidLevel, raidBoss)
                    })
                }

                details.push({
                    name: gymIconName(teamId, 0, raidLevel, unknownRaidBoss),
                    teamId: teamId,
                    gymStrength: 0,
                    raidLevel: raidLevel,
                    raidBoss: unknownRaidBoss,
                    resourceDetails: gymResourceDetails(teamId, 0, raidLevel, unknownRaidBoss)
                })
            }
        }
    }

    // Only contested gyms
    for (teamId = 1; teamId < teams.length; ++teamId) {
        // Plain gym icon
        details.push({
            name: gymIconName(teamId),
            teamId: teamId,
            resourceDetails: gymResourceDetails(teamId)
        })

        // Gym icons with pokemon and raid eggs
        for (var gymStrength = 0; gymStrength <= 6; ++gymStrength) {
            for (raidLevel = 0; raidLevel <= 5; ++raidLevel) {
                details.push({
                    name: gymIconName(teamId, gymStrength, raidLevel),
                    teamId: teamId,
                    gymStrength: gymStrength,
                    raidLevel: raidLevel,
                    resourceDetails: gymResourceDetails(teamId, gymStrength, raidLevel)
                })
            }
        }
    }

    return details
}

function buildResourceMap(resources) {
    const resourceMap = {}

    resources.forEach(function (resource) {
        const type = resource[0]
        const path = resource[1]

        const resourceDetails = {
            type: type,
            path: path,
            name: resource[2]
        }

        switch (type) {
            case 'icon':
                var icon = resource[3]
                const size = resource[4]

                if (size && (icon.bitmap.width !== size[0] ||
                             icon.bitmap.height !== size[1])) {
                    icon = icon.resize(size[0], size[1])
                               .background(0x0)
                }

                resourceDetails.resource = icon
                resourceDetails.size = size
                break

            case 'font':
                resourceDetails.resource = resource[3]
                break
        }

        resourceMap[resourceDetailsHash(resourceDetails)] = resourceDetails
    })

    return resourceMap
}

function resourcesForIcon(iconDetails, resourceMap) {
    const iconResources = {}
    iconDetails.resourceDetails.forEach(function (details) {
        const resource = resourceMap[resourceDetailsHash(details)].resource
        iconResources[details.name] = resource
    })
    return iconResources
}

function createProgressBar(text, size, stream = process.stdout) {
    readline.clearLine(stream, 0)
    stream.write(`${text} [${' '.repeat(size)}]\n`)
    readline.moveCursor(stream, 0, -1)
    readline.cursorTo(stream, text.length + 2)
}

function updateProgressBar(stream = process.stdout) {
    stream.write('=')
}

function endProgressBar(stream = process.stdout) {
    readline.cursorTo(stream, 0)
    readline.clearLine(stream, 0)
}

function buildPokemonIcon(iconDetails, resources) {
    return new Promise(function (resolve, reject) {
        // eslint-disable-next-line no-new
        new Jimp(192, 192, function (err, icon) {
            if (err) {
                reject(err)
            }

            const pokemon = iconDetails.pokemon
            const form = iconDetails.form

            const circle = resources['circle']
            const font = resources['font']

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
                icon.print(font,
                           (pokemonBkg.bitmap.width / 2) -
                           (textWidth(font, idText) / 2),
                           (pokemonBkg.bitmap.height / 2) -
                           textHeight(font, idText) -
                           7,
                           idText)
                icon.print(font,
                           (pokemonBkg.bitmap.width / 2) -
                           (textWidth(font, formText) / 2),
                           (pokemonBkg.bitmap.height / 2) +
                           7,
                           formText)
            } else {
                // Just ID
                icon.print(font,
                           (pokemonBkg.bitmap.width / 2) -
                           (textWidth(font, idText) / 2),
                           (pokemonBkg.bitmap.height / 2) -
                           (textHeight(font, idText) / 2),
                           idText)
            }

            icon.write(`${pokemonDir}/${iconDetails.name}.png`, function () {
                resolve(iconDetails.name)
            })
        })
    })
}

function buildGymIcon(iconDetails, resources) {
    return new Promise(function (resolve, reject) {
        // eslint-disable-next-line no-new
        new Jimp(192, 192, function (err, icon) {
            if (err) {
                reject(err)
            }

            const teamId = iconDetails.teamId
            const gymStrength = iconDetails.gymStrength
            const raidLevel = iconDetails.raidLevel
            const raidBoss = iconDetails.raidBoss

            const circle = resources['small_circle']
            const circleBorder = resources['circle_border']
            const largeCircle = resources['large_circle']
            const font = resources['font']

            const gym = resources['gym']
            icon = icon.composite(gym,
                                  (icon.bitmap.width / 2) - (gym.bitmap.width / 2),
                                  (icon.bitmap.height / 2) - (gym.bitmap.height / 2))

            // Raid egg
            const raidEgg = resources['raid_egg']
            if (raidLevel && raidLevel > 0 && !raidBoss) {
                icon = icon.composite(raidEgg,
                                      icon.bitmap.width - raidEgg.bitmap.width - 3,
                                      icon.bitmap.height - raidEgg.bitmap.height - 12)
            }

            // Raid boss
            if (raidBoss) {
                if (raidBoss === 'unknown') {
                    const unknownRaidBossBkg = largeCircle.clone()
                                                          .color([{
                                                              apply: 'mix',
                                                              params: ['#C0C0C0', 100]
                                                          }])
                                                          .background(0x0)

                    icon = icon.composite(unknownRaidBossBkg,
                                          0,
                                          icon.bitmap.height -
                                          unknownRaidBossBkg.bitmap.height)
                    icon.print(font,
                               (unknownRaidBossBkg.bitmap.width / 2) -
                               (textWidth(font, unknownRaidBossText) / 2),
                               icon.bitmap.height -
                               (unknownRaidBossBkg.bitmap.height / 2) -
                               (textHeight(font, unknownRaidBossText) / 2),
                               unknownRaidBossText)
                } else {
                    const raidBossIcon = resources['raid_boss']
                    icon = icon.composite(raidBossIcon,
                                          0,
                                          icon.bitmap.height -
                                          raidBossIcon.bitmap.height)
                }
            }

            // Gym strength
            const gymStrengthY = icon.bitmap.height -
                                 (circleBorder.bitmap.height / 1.75) -
                                 4

            if (gymStrength && gymStrength > 0 && !raidBoss) {
                const gymStrengthBkg = circle.clone()
                                             .color([{
                                                 apply: 'mix',
                                                 params: [teamColors[teamId], 100]
                                             }])
                                             .background(0x0)

                var gymStrengthX
                if (raidLevel && raidLevel > 0) {
                    gymStrengthX = (icon.bitmap.width / 2) -
                                  (gymStrengthBkg.bitmap.width / 2) +
                                  9
                } else {
                    gymStrengthX = (icon.bitmap.width / 2) - 6
                }

                icon = icon.composite(gymStrengthBkg,
                                      gymStrengthX - (gymStrengthBkg.bitmap.width / 2),
                                      gymStrengthY - (gymStrengthBkg.bitmap.height / 2))
                icon = icon.composite(circleBorder,
                                      gymStrengthX - (circleBorder.bitmap.width / 2),
                                      gymStrengthY - (circleBorder.bitmap.height / 2))
            }

            // Raid level
            if (raidLevel && raidLevel > 0) {
                const raidLevelBkg = resources['raid_star'].clone()
                const raidLevelNum = resources['raid_level']
                const raidLevelHeight = icon.bitmap.height - (raidLevelBkg.bitmap.height / 2)

                icon = icon.composite(raidLevelBkg,
                                      icon.bitmap.width -
                                      (raidEgg.bitmap.width / 2) -
                                      (raidLevelBkg.bitmap.width / 2) +
                                      10,
                                      raidLevelHeight -
                                      (raidLevelBkg.bitmap.height / 2))
                icon = icon.composite(raidLevelNum,
                                      icon.bitmap.width -
                                      (raidEgg.bitmap.width / 2) -
                                      (raidLevelNum.bitmap.width / 2) +
                                      10,
                                      raidLevelHeight -
                                      (raidLevelNum.bitmap.height / 2) +
                                      5)
            }

            // Gym strength number
            if (gymStrength && gymStrength > 0 && !raidBoss) {
                const gymStrengthNum = resources['gym_strength']
                icon = icon.composite(gymStrengthNum,
                                      gymStrengthX - (gymStrengthNum.bitmap.width / 2),
                                      gymStrengthY - (gymStrengthNum.bitmap.height / 2))
            }

            icon.write(`${gymsDir}/${iconDetails.name}.png`, function () {
                resolve(iconDetails.name)
            })
        })
    })
}

module.exports = function () {
    const done = this.async()

    const pokemonIconDetails = getPokemonIconDetails().filter(function (iconDetails) {
        return !iconAlreadyExists('pokemon', iconDetails.name) ||
               resourceChanged(iconDetails.resourceDetails)
    })

    const pokemonResourceDetails = {}
    pokemonIconDetails.forEach(function (iconDetails) {
        iconDetails.resourceDetails.forEach(function (details) {
            pokemonResourceDetails[resourceDetailsHash(details)] = details
        })
    })

    const gymIconDetails = getGymIconDetails().filter(function (iconDetails) {
        return !iconAlreadyExists('gyms', iconDetails.name) ||
               resourceChanged(iconDetails.resourceDetails)
    })

    const gymResourceDetails = {}
    gymIconDetails.forEach(function (iconDetails) {
        iconDetails.resourceDetails.forEach(function (details) {
            gymResourceDetails[resourceDetailsHash(details)] = details
        })
    })

    const pokemonResourcePromises = []
    for (var item in pokemonResourceDetails) {
        const resourceDetails = pokemonResourceDetails[item]
        pokemonResourcePromises.push(resourcePromise(resourceDetails))
    }

    Promise.all(pokemonResourcePromises)
    .then(function (resources) {
        const resourceMap = buildResourceMap(resources)

        const pokemonIconDetailsBatches = []
        const numBatches = Math.ceil(pokemonIconDetails.length / batchSize)
        for (var i = 0; i < numBatches; ++i) {
            const batchStart = i * batchSize
            const batch = pokemonIconDetails.slice(batchStart, batchStart + batchSize)
            pokemonIconDetailsBatches.push(batch)
        }

        createProgressBar('>> building pokemon icons', numBatches)

        var iconsCreated = 0
        return pokemonIconDetailsBatches.reduce(function (prev, pokemonIconDetails) {
            return prev
            .then(function () {
                return Promise.all(pokemonIconDetails.map(function (iconDetails) {
                    const iconResources = resourcesForIcon(iconDetails, resourceMap)
                    return buildPokemonIcon(iconDetails, iconResources)
                }))
            })
            .then(function (results) {
                iconsCreated += results.length
                updateProgressBar()
            })
        }, Promise.resolve(1))
        .then(function () {
            endProgressBar()
            return iconsCreated
        })
    })
    .then(function (iconsCreated) {
        console.log('>>'['green'] + ` ${iconsCreated} pokemon icons built.`)

        const gymResourcePromises = []
        for (var item in gymResourceDetails) {
            const resourceDetails = gymResourceDetails[item]
            gymResourcePromises.push(resourcePromise(resourceDetails))
        }

        return Promise.all(gymResourcePromises)
    })
    .then(function (resources) {
        const resourceMap = buildResourceMap(resources)

        const gymIconDetailsBatches = []
        const numBatches = Math.ceil(gymIconDetails.length / batchSize)
        for (var i = 0; i < numBatches; ++i) {
            const batchStart = i * batchSize
            const batch = gymIconDetails.slice(batchStart, batchStart + batchSize)
            gymIconDetailsBatches.push(batch)
        }

        createProgressBar('>> building gym icons', numBatches)

        var iconsCreated = 0
        return gymIconDetailsBatches.reduce(function (prev, gymIconDetails) {
            return prev
            .then(function () {
                return Promise.all(gymIconDetails.map(function (iconDetails) {
                    const iconResources = resourcesForIcon(iconDetails, resourceMap)
                    return buildGymIcon(iconDetails, iconResources)
                }))
            })
            .then(function (results) {
                iconsCreated += results.length
                updateProgressBar()
            })
        }, Promise.resolve(1))
        .then(function () {
            endProgressBar()
            return iconsCreated
        })
    })
    .then(function () {
        console.log('>>'['green'] + ` ${gymIconDetails.length} gym icons built.`)
        saveResourceInfo()
        done()
    })
    .catch(function (err) {
        console.log('>> '['red'] + (err.stack || err))
        done(false)
    })
}

module.exports = function (grunt) {

    // load plugins as needed instead of up front
    require('jit-grunt')(grunt, {
        unzip: 'grunt-zip',
        sprite: 'grunt-spritesmith'
    })

    var path = require('path')
    var fs = require('fs')
    var Jimp = require('jimp')
    var Promise = require('grunt-promise').using('bluebird')

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        sass: {
            dist: {
                files: {
                    'static/dist/css/app.built.css': 'static/sass/main.scss',
                    'static/dist/css/mobile.built.css': 'static/sass/mobile.scss',
                    'static/dist/css/statistics.built.css': 'static/sass/statistics.scss',
                    'static/dist/css/status.built.css': 'static/sass/status.scss'
                }
            }
        },
        eslint: {
            src: ['static/js/*.js', '!static/js/vendor/**/*.js']
        },
        babel: {
            options: {
                sourceMap: true,
                presets: [
                    ['env', {
                        'targets': {
                            'browsers': ['>0.5%']
                        }
                    }]
                ]
            },
            dist: {
                files: {
                    'static/dist/js/app.built.js': 'static/js/app.js',
                    'static/dist/js/map.built.js': 'static/js/map.js',
                    'static/dist/js/map.common.built.js': 'static/js/map.common.js',
                    'static/dist/js/mobile.built.js': 'static/js/mobile.js',
                    'static/dist/js/stats.built.js': 'static/js/stats.js',
                    'static/dist/js/statistics.built.js': 'static/js/statistics.js',
                    'static/dist/js/status.built.js': 'static/js/status.js',
                    'static/dist/js/custom.built.js': 'static/js/custom.js',
                    'static/dist/js/vendor/markerclusterer.built.js': 'static/js/vendor/markerclusterer.js',
                    'static/dist/js/serviceWorker.built.js': 'static/js/serviceWorker.js'
                }
            }
        },
        uglify: {
            options: {
                banner: '/*\n <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> \n*/\n',
                sourceMap: true,
                compress: {
                    unused: false
                }
            },
            build: {
                files: {
                    'static/dist/js/app.min.js': 'static/dist/js/app.built.js',
                    'static/dist/js/map.min.js': 'static/dist/js/map.built.js',
                    'static/dist/js/map.common.min.js': 'static/dist/js/map.common.built.js',
                    'static/dist/js/mobile.min.js': 'static/dist/js/mobile.built.js',
                    'static/dist/js/stats.min.js': 'static/dist/js/stats.built.js',
                    'static/dist/js/statistics.min.js': 'static/dist/js/statistics.built.js',
                    'static/dist/js/status.min.js': 'static/dist/js/status.built.js',
                    'static/dist/js/custom.min.js': 'static/dist/js/custom.built.js',
                    'static/dist/js/vendor/markerclusterer.min.js': 'static/dist/js/vendor/markerclusterer.built.js',
                    'static/dist/js/serviceWorker.min.js': 'static/dist/js/serviceWorker.built.js'
                }
            }
        },
        minjson: {
            build: {
                files: {
                    'static/dist/data/pokemon.min.json': 'static/data/pokemon.json',
                    'static/dist/data/moves.min.json': 'static/data/moves.json',
                    'static/dist/data/mapstyle.min.json': 'static/data/mapstyle.json',
                    'static/dist/data/searchmarkerstyle.min.json': 'static/data/searchmarkerstyle.json',
                    'static/dist/data/sprites_map.min.json': 'static/data/sprites_map.json',
                    'static/dist/locales/de.min.json': 'static/locales/de.json',
                    'static/dist/locales/fr.min.json': 'static/locales/fr.json',
                    'static/dist/locales/ja.min.json': 'static/locales/ja.json',
                    'static/dist/locales/ko.min.json': 'static/locales/ko.json',
                    'static/dist/locales/pt_br.min.json': 'static/locales/pt_br.json',
                    'static/dist/locales/ru.min.json': 'static/locales/ru.json',
                    'static/dist/locales/zh_cn.min.json': 'static/locales/zh_cn.json',
                    'static/dist/locales/zh_tw.min.json': 'static/locales/zh_tw.json',
                    'static/dist/locales/zh_hk.min.json': 'static/locales/zh_hk.json'
                }
            }
        },
        clean: {
            build: {
                src: 'static/dist'
            }
        },
        watch: {
            options: {
                interval: 1000,
                spawn: true
            },
            js: {
                files: ['static/js/**/*.js'],
                options: {livereload: true},
                tasks: ['js-lint', 'js-build']
            },
            json: {
                files: ['static/data/*.json', 'static/locales/*.json'],
                options: {livereload: true},
                tasks: ['json']
            },
            css: {
                files: '**/*.scss',
                options: {livereload: true},
                tasks: ['css-build']
            }
        },
        cssmin: {
            options: {
                banner: '/*\n <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> \n*/\n'
            },
            build: {
                files: {
                    'static/dist/css/app.min.css': 'static/dist/css/app.built.css',
                    'static/dist/css/mobile.min.css': 'static/dist/css/mobile.built.css',
                    'static/dist/css/statistics.min.css': 'static/dist/css/statistics.built.css',
                    'static/dist/css/status.min.css': 'static/dist/css/status.built.css'
                }
            }
        },
        unzip: {
            'static01': {
                router: function (filepath) {
                    if (fs.existsSync('static/' + filepath)) {
                        return null
                    }

                    return filepath
                },

                src: 'static01.zip',
                dest: 'static/'
            }
        },
        sprite: {
            scss: {
                src: [
                    'static/icons/pokemon/*.png',
                    'static/icons/gyms/*.png'
                ],
                dest: 'static/spritesheet.png',
                destCss: 'static/sass/sprites.scss',
                cssTemplate: 'static/spritesheet.scss.hbs',
                engine: 'canvassmith'
            },
            json: {
                src: [
                    'static/icons/pokemon/*.png',
                    'static/icons/gyms/*.png'
                ],
                dest: 'static/spritesheet.png',
                destCss: 'static/data/sprites_map.json',
                cssTemplate: 'static/sprites_map.json.hbs',
                engine: 'canvassmith'
            }
        }
    })

    grunt.registerTask('js-build', ['newer:babel', 'newer:uglify'])
    grunt.registerTask('css-build', ['newer:sass', 'newer:cssmin'])
    grunt.registerTask('js-lint', ['newer:eslint'])
    grunt.registerTask('json', ['newer:minjson'])

    grunt.registerPromise('build-icons', 'Builds the icons for gyms and raids.', function() {
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

        function generateGymIcon(iconMap, teamId, numPokemon, raidLevel, raidBoss) {
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

                    // Raid boss
                    if (raidBoss) {
                        var raidBossIcon = iconMap[`raid_boss_${raidBoss}`]
                        icon = icon.composite(raidBossIcon,
                                              0,
                                              icon.bitmap.height - raidBossIcon.bitmap.height)
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


        const iconPromisesMap = [
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
            iconPromisesMap.push({
                name: `number_${i}`,
                promise: Jimp.read(`${partsDir}/${i}.png`),
                size: [60, 60]
            })
        }

        for (var t = 0; t < teams.length; ++t) {
            iconPromisesMap.push({
                name: `gym_${teams[t]}`,
                promise: Jimp.read(`${partsDir}/gym_${teams[t]}.png`),
                size: [175, 175]
            })
        }

        for (var raidLevel = 1; raidLevel <= 5; ++raidLevel) {
            iconPromisesMap.push({
                name: `raid_egg_${raidLevel}`,
                promise: Jimp.read(`${partsDir}/raid_egg_${raidLevel}.png`),
                size: [110, 110]
            })

            for (var raidBoss in raidBosses[raidLevel]) {
                raidBoss = raidBosses[raidLevel][raidBoss]
                iconPromisesMap.push({
                    name: `raid_boss_${raidBoss}`,
                    promise: Jimp.read(`${pokemonDir}/${raidBoss}.png`),
                    size: [100, 100]
                })
            }
        }

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

                for (var teamId = 0; teamId < teams.length; ++teamId) {
                    for (var raidLevel = 0; raidLevel <= 5; ++raidLevel) {
                        generationPromises.push(
                            generateGymIcon(iconMap, teamId, 0, raidLevel))
                    
                        if (raidLevel > 0) {
                            for (var raidBoss in raidBosses[raidLevel]) {
                                raidBoss = raidBosses[raidLevel][raidBoss]
                                generationPromises.push(
                                    generateGymIcon(iconMap, teamId, 0, raidLevel, raidBoss))
                            }
                        }
                    }
                }

                for (var teamId = 1; teamId < teams.length; ++teamId) {
                    generationPromises.push(generateGymIcon(iconMap, teamId))

                    for (var numPokemon = 0; numPokemon <= 6; ++numPokemon) {
                        for (var raidLevel = 0; raidLevel <= 5; ++raidLevel) {
                            generationPromises.push(
                                generateGymIcon(iconMap, teamId, numPokemon, raidLevel))
                        }
                    }
                }

                //generationPromises.push(
                //    generateGymIcon(iconMap, t, numPokemon, raidLevel, raidBoss))
                
                Promise.all(generationPromises)
                .then(function() {
                    resolve()
                })
            }).catch(function (err) {
                reject(err)
            })
        })
    })

    grunt.registerTask('build', ['clean', 'js-build', 'css-build', 'json'])
    grunt.registerTask('lint', ['js-lint'])
    grunt.registerTask('default', ['build', 'watch'])
}

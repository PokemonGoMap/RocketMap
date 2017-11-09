'use strict'

const Promise = require('bluebird')
const glob = require('glob')
const fs = require('fs')
const Spritesmith = require('spritesmith')
const Handlebars = require('handlebars')

const spritesheetIcons = 'static/icons'
const spritesheetFile = 'static/spritesheet.png'
const spritesheetScssFile = 'static/sass/sprites.scss'
const spritesheetScssTemplate = 'templates/sprites.scss.hbs'
const spritesheetMapFile = 'static/data/sprite_map.json'

const writeFile = Promise.promisify(fs.writeFile)

function writeSpritesheetToFile(spritesheet, file) {
    return new Promise(function (resolve, reject) {
        const stream = fs.createWriteStream(file)
        stream.on('finish', resolve)
        stream.on('error', reject)
        spritesheet.pipe(stream)
    })
}

function writeSpritesheetScssToFile(spritesheetMap, file) {
    const templateFile = fs.readFileSync(spritesheetScssTemplate, 'utf8')
    const template = Handlebars.compile(templateFile)
    const spritesheetScss = template(spritesheetMap)
    return writeFile(file, spritesheetScss)
}

function writeSpritesheetMapToFile(spritesheetMap, file) {
    return writeFile(file, JSON.stringify(spritesheetMap, null, 2))
}

module.exports = function () {
    const sprites = glob.sync(`${spritesheetIcons}/**/*.png`, {
        ignore: `${spritesheetIcons}/parts/**/*.png`
    })

    const spritesmith = new Spritesmith({
        engine: 'canvassmith'
    })

    return new Promise(function (resolve, reject) {
        spritesmith.createImages(sprites, function (err, images) {
            if (err) {
                reject(err)
            }
            resolve(spritesmith.processImages(images))
        })
    })
    .then(function (spritesheetData) {
        const spritesheetInfo = spritesheetData.properties
        spritesheetInfo.url = spritesheetFile

        const spriteInfo = {}
        for (var spritePath in spritesheetData.coordinates) {
            var spriteName = spritePath.replace(`${spritesheetIcons}/`, '')
                                       .replace(/\.[^/.]+$/, '')
                                       .replace('/', '-')
            spriteInfo[spriteName] = spritesheetData.coordinates[spritePath]
        }

        const spritesheetMap = {
            spritesheet: spritesheetInfo,
            sprites: spriteInfo
        }

        return Promise.all([
            writeSpritesheetToFile(spritesheetData.image, spritesheetFile),
            writeSpritesheetScssToFile(spritesheetMap, spritesheetScssFile),
            writeSpritesheetMapToFile(spritesheetMap, spritesheetMapFile)
        ])
    })
    .then(function () {
        console.log('>> '['green'] + 'spritesheet built.')
    })
    .catch(function (err) {
        console.log('>> '['red'] + (err.stack || err))
        throw err
    })
}

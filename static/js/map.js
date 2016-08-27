//
// Global map.js variables
//

var $selectExclude
var $selectPokemonNotify
var $selectRarityNotify
var $selectStyle
var $selectIconResolution
var $selectIconSize
var $selectLuredPokestopsOnly
var $selectSearchIconMarker
var $selectSoundNotify
var $selectAudiospriteNotify
var $selectNotificationNotify
var $selectTexttospeechNotify
var $selectNearbyNotify
var $selectNearbyDistanceNotify

var language = document.documentElement.lang === '' ? 'en' : document.documentElement.lang
var idToPokemon = {}
var i8lnDictionary = {}
var notificationDistances = {}
var audiosprites = {}
var pushNotify = new PushNotification(5)
var soundNotify = new SoundNotification(5)
var textToSpeechNotify = new TextToSpeechNotification(5)
var languageLookups = 0
var languageLookupThreshold = 3

var searchMarkerStyles

var excludedPokemon = []
var notifiedPokemon = []
var notifiedRarity = []

var map
var rawDataIsLoading = false
var locationMarker
var rangeMarkers = ['pokemon', 'pokestop', 'gym']
var searchMarker
var storeZoom = true

var noLabelsStyle = [{
  featureType: 'poi',
  elementType: 'labels',
  stylers: [{
    visibility: 'off'
  }]
}, {
  'featureType': 'all',
  'elementType': 'labels.text.stroke',
  'stylers': [{
    'visibility': 'off'
  }]
}, {
  'featureType': 'all',
  'elementType': 'labels.text.fill',
  'stylers': [{
    'visibility': 'off'
  }]
}, {
  'featureType': 'all',
  'elementType': 'labels.icon',
  'stylers': [{
    'visibility': 'off'
  }]
}]
var light2Style = [{
  'elementType': 'geometry',
  'stylers': [{
    'hue': '#ff4400'
  }, {
    'saturation': -68
  }, {
    'lightness': -4
  }, {
    'gamma': 0.72
  }]
}, {
  'featureType': 'road',
  'elementType': 'labels.icon'
}, {
  'featureType': 'landscape.man_made',
  'elementType': 'geometry',
  'stylers': [{
    'hue': '#0077ff'
  }, {
    'gamma': 3.1
  }]
}, {
  'featureType': 'water',
  'stylers': [{
    'hue': '#00ccff'
  }, {
    'gamma': 0.44
  }, {
    'saturation': -33
  }]
}, {
  'featureType': 'poi.park',
  'stylers': [{
    'hue': '#44ff00'
  }, {
    'saturation': -23
  }]
}, {
  'featureType': 'water',
  'elementType': 'labels.text.fill',
  'stylers': [{
    'hue': '#007fff'
  }, {
    'gamma': 0.77
  }, {
    'saturation': 65
  }, {
    'lightness': 99
  }]
}, {
  'featureType': 'water',
  'elementType': 'labels.text.stroke',
  'stylers': [{
    'gamma': 0.11
  }, {
    'weight': 5.6
  }, {
    'saturation': 99
  }, {
    'hue': '#0091ff'
  }, {
    'lightness': -86
  }]
}, {
  'featureType': 'transit.line',
  'elementType': 'geometry',
  'stylers': [{
    'lightness': -48
  }, {
    'hue': '#ff5e00'
  }, {
    'gamma': 1.2
  }, {
    'saturation': -23
  }]
}, {
  'featureType': 'transit',
  'elementType': 'labels.text.stroke',
  'stylers': [{
    'saturation': -64
  }, {
    'hue': '#ff9100'
  }, {
    'lightness': 16
  }, {
    'gamma': 0.47
  }, {
    'weight': 2.7
  }]
}]
var darkStyle = [{
  'featureType': 'all',
  'elementType': 'labels.text.fill',
  'stylers': [{
    'saturation': 36
  }, {
    'color': '#b39964'
  }, {
    'lightness': 40
  }]
}, {
  'featureType': 'all',
  'elementType': 'labels.text.stroke',
  'stylers': [{
    'visibility': 'on'
  }, {
    'color': '#000000'
  }, {
    'lightness': 16
  }]
}, {
  'featureType': 'all',
  'elementType': 'labels.icon',
  'stylers': [{
    'visibility': 'off'
  }]
}, {
  'featureType': 'administrative',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#000000'
  }, {
    'lightness': 20
  }]
}, {
  'featureType': 'administrative',
  'elementType': 'geometry.stroke',
  'stylers': [{
    'color': '#000000'
  }, {
    'lightness': 17
  }, {
    'weight': 1.2
  }]
}, {
  'featureType': 'landscape',
  'elementType': 'geometry',
  'stylers': [{
    'color': '#000000'
  }, {
    'lightness': 20
  }]
}, {
  'featureType': 'poi',
  'elementType': 'geometry',
  'stylers': [{
    'color': '#000000'
  }, {
    'lightness': 21
  }]
}, {
  'featureType': 'road.highway',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#000000'
  }, {
    'lightness': 17
  }]
}, {
  'featureType': 'road.highway',
  'elementType': 'geometry.stroke',
  'stylers': [{
    'color': '#000000'
  }, {
    'lightness': 29
  }, {
    'weight': 0.2
  }]
}, {
  'featureType': 'road.arterial',
  'elementType': 'geometry',
  'stylers': [{
    'color': '#000000'
  }, {
    'lightness': 18
  }]
}, {
  'featureType': 'road.local',
  'elementType': 'geometry',
  'stylers': [{
    'color': '#181818'
  }, {
    'lightness': 16
  }]
}, {
  'featureType': 'transit',
  'elementType': 'geometry',
  'stylers': [{
    'color': '#000000'
  }, {
    'lightness': 19
  }]
}, {
  'featureType': 'water',
  'elementType': 'geometry',
  'stylers': [{
    'lightness': 17
  }, {
    'color': '#525252'
  }]
}]
var pGoStyle = [{
  'featureType': 'landscape.man_made',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#a1f199'
  }]
}, {
  'featureType': 'landscape.natural.landcover',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#37bda2'
  }]
}, {
  'featureType': 'landscape.natural.terrain',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#37bda2'
  }]
}, {
  'featureType': 'poi.attraction',
  'elementType': 'geometry.fill',
  'stylers': [{
    'visibility': 'on'
  }]
}, {
  'featureType': 'poi.business',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#e4dfd9'
  }]
}, {
  'featureType': 'poi.business',
  'elementType': 'labels.icon',
  'stylers': [{
    'visibility': 'off'
  }]
}, {
  'featureType': 'poi.park',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#37bda2'
  }]
}, {
  'featureType': 'road',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#84b09e'
  }]
}, {
  'featureType': 'road',
  'elementType': 'geometry.stroke',
  'stylers': [{
    'color': '#fafeb8'
  }, {
    'weight': '1.25'
  }]
}, {
  'featureType': 'road.highway',
  'elementType': 'labels.icon',
  'stylers': [{
    'visibility': 'off'
  }]
}, {
  'featureType': 'water',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#5ddad6'
  }]
}]
var light2StyleNoLabels = [{
  'elementType': 'geometry',
  'stylers': [{
    'hue': '#ff4400'
  }, {
    'saturation': -68
  }, {
    'lightness': -4
  }, {
    'gamma': 0.72
  }]
}, {
  'featureType': 'road',
  'elementType': 'labels.icon'
}, {
  'featureType': 'landscape.man_made',
  'elementType': 'geometry',
  'stylers': [{
    'hue': '#0077ff'
  }, {
    'gamma': 3.1
  }]
}, {
  'featureType': 'water',
  'stylers': [{
    'hue': '#00ccff'
  }, {
    'gamma': 0.44
  }, {
    'saturation': -33
  }]
}, {
  'featureType': 'poi.park',
  'stylers': [{
    'hue': '#44ff00'
  }, {
    'saturation': -23
  }]
}, {
  'featureType': 'water',
  'elementType': 'labels.text.fill',
  'stylers': [{
    'hue': '#007fff'
  }, {
    'gamma': 0.77
  }, {
    'saturation': 65
  }, {
    'lightness': 99
  }]
}, {
  'featureType': 'water',
  'elementType': 'labels.text.stroke',
  'stylers': [{
    'gamma': 0.11
  }, {
    'weight': 5.6
  }, {
    'saturation': 99
  }, {
    'hue': '#0091ff'
  }, {
    'lightness': -86
  }]
}, {
  'featureType': 'transit.line',
  'elementType': 'geometry',
  'stylers': [{
    'lightness': -48
  }, {
    'hue': '#ff5e00'
  }, {
    'gamma': 1.2
  }, {
    'saturation': -23
  }]
}, {
  'featureType': 'transit',
  'elementType': 'labels.text.stroke',
  'stylers': [{
    'saturation': -64
  }, {
    'hue': '#ff9100'
  }, {
    'lightness': 16
  }, {
    'gamma': 0.47
  }, {
    'weight': 2.7
  }]
}, {
  'featureType': 'all',
  'elementType': 'labels.text.stroke',
  'stylers': [{
    'visibility': 'off'
  }]
}, {
  'featureType': 'all',
  'elementType': 'labels.text.fill',
  'stylers': [{
    'visibility': 'off'
  }]
}, {
  'featureType': 'all',
  'elementType': 'labels.icon',
  'stylers': [{
    'visibility': 'off'
  }]
}]
var darkStyleNoLabels = [{
  'featureType': 'all',
  'elementType': 'labels.text.fill',
  'stylers': [{
    'visibility': 'off'
  }]
}, {
  'featureType': 'all',
  'elementType': 'labels.text.stroke',
  'stylers': [{
    'visibility': 'off'
  }]
}, {
  'featureType': 'all',
  'elementType': 'labels.icon',
  'stylers': [{
    'visibility': 'off'
  }]
}, {
  'featureType': 'administrative',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#000000'
  }, {
    'lightness': 20
  }]
}, {
  'featureType': 'administrative',
  'elementType': 'geometry.stroke',
  'stylers': [{
    'color': '#000000'
  }, {
    'lightness': 17
  }, {
    'weight': 1.2
  }]
}, {
  'featureType': 'landscape',
  'elementType': 'geometry',
  'stylers': [{
    'color': '#000000'
  }, {
    'lightness': 20
  }]
}, {
  'featureType': 'poi',
  'elementType': 'geometry',
  'stylers': [{
    'color': '#000000'
  }, {
    'lightness': 21
  }]
}, {
  'featureType': 'road.highway',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#000000'
  }, {
    'lightness': 17
  }]
}, {
  'featureType': 'road.highway',
  'elementType': 'geometry.stroke',
  'stylers': [{
    'color': '#000000'
  }, {
    'lightness': 29
  }, {
    'weight': 0.2
  }]
}, {
  'featureType': 'road.arterial',
  'elementType': 'geometry',
  'stylers': [{
    'color': '#000000'
  }, {
    'lightness': 18
  }]
}, {
  'featureType': 'road.local',
  'elementType': 'geometry',
  'stylers': [{
    'color': '#181818'
  }, {
    'lightness': 16
  }]
}, {
  'featureType': 'transit',
  'elementType': 'geometry',
  'stylers': [{
    'color': '#000000'
  }, {
    'lightness': 19
  }]
}, {
  'featureType': 'water',
  'elementType': 'geometry',
  'stylers': [{
    'lightness': 17
  }, {
    'color': '#525252'
  }]
}]
var pGoStyleNoLabels = [{
  'featureType': 'landscape.man_made',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#a1f199'
  }]
}, {
  'featureType': 'landscape.natural.landcover',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#37bda2'
  }]
}, {
  'featureType': 'landscape.natural.terrain',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#37bda2'
  }]
}, {
  'featureType': 'poi.attraction',
  'elementType': 'geometry.fill',
  'stylers': [{
    'visibility': 'on'
  }]
}, {
  'featureType': 'poi.business',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#e4dfd9'
  }]
}, {
  'featureType': 'poi.business',
  'elementType': 'labels.icon',
  'stylers': [{
    'visibility': 'off'
  }]
}, {
  'featureType': 'poi.park',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#37bda2'
  }]
}, {
  'featureType': 'road',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#84b09e'
  }]
}, {
  'featureType': 'road',
  'elementType': 'geometry.stroke',
  'stylers': [{
    'color': '#fafeb8'
  }, {
    'weight': '1.25'
  }]
}, {
  'featureType': 'road.highway',
  'elementType': 'labels.icon',
  'stylers': [{
    'visibility': 'off'
  }]
}, {
  'featureType': 'water',
  'elementType': 'geometry.fill',
  'stylers': [{
    'color': '#5ddad6'
  }]
}, {
  'featureType': 'all',
  'elementType': 'labels.text.stroke',
  'stylers': [{
    'visibility': 'off'
  }]
}, {
  'featureType': 'all',
  'elementType': 'labels.text.fill',
  'stylers': [{
    'visibility': 'off'
  }]
}, {
  'featureType': 'all',
  'elementType': 'labels.icon',
  'stylers': [{
    'visibility': 'off'
  }]
}]

var selectedStyle = 'light'

var mapData = {
  pokemons: {},
  gyms: {},
  pokestops: {},
  lurePokemons: {},
  scanned: {},
  spawnpoints: {}
}
var gymTypes = ['Uncontested', 'Mystic', 'Valor', 'Instinct']
var pokemonSprites = {
  normal: {
    columns: 12,
    iconWidth: 30,
    iconHeight: 30,
    spriteWidth: 360,
    spriteHeight: 390,
    filename: 'static/icons-sprite.png',
    name: 'Normal'
  },
  highres: {
    columns: 7,
    iconWidth: 65,
    iconHeight: 65,
    spriteWidth: 455,
    spriteHeight: 1430,
    filename: 'static/icons-large-sprite.png',
    name: 'High-Res'
  },
  shuffle: {
    columns: 7,
    iconWidth: 65,
    iconHeight: 65,
    spriteWidth: 455,
    spriteHeight: 1430,
    filename: 'static/icons-shuffle-sprite.png',
    name: 'Shuffle'
  }
}

//
// LocalStorage helpers
//

var StoreTypes = {
  Boolean: {
    parse: function (str) {
      switch (str.toLowerCase()) {
        case '1':
        case 'true':
        case 'yes':
          return true
        default:
          return false
      }
    },
    stringify: function (b) {
      return b ? 'true' : 'false'
    }
  },
  JSON: {
    parse: function (str) {
      return JSON.parse(str)
    },
    stringify: function (json) {
      return JSON.stringify(json)
    }
  },
  String: {
    parse: function (str) {
      return str
    },
    stringify: function (str) {
      return str
    }
  },
  Number: {
    parse: function (str) {
      return parseInt(str, 10)
    },
    stringify: function (number) {
      return number.toString()
    }
  }
}

var StoreOptions = {
  'map_style': {
    default: 'roadmap',
    type: StoreTypes.String
  },
  'remember_select_exclude': {
    default: [],
    type: StoreTypes.JSON
  },
  'remember_select_notify': {
    default: [],
    type: StoreTypes.JSON
  },
  'remember_select_rarity_notify': {
    default: [],
    type: StoreTypes.JSON
  },
  'showGyms': {
    default: false,
    type: StoreTypes.Boolean
  },
  'showPokemon': {
    default: true,
    type: StoreTypes.Boolean
  },
  'showPokestops': {
    default: true,
    type: StoreTypes.Boolean
  },
  'showLuredPokestopsOnly': {
    default: 0,
    type: StoreTypes.Number
  },
  'showScanned': {
    default: false,
    type: StoreTypes.Boolean
  },
  'showSpawnpoints': {
    default: false,
    type: StoreTypes.Boolean
  },
  'showRanges': {
    default: false,
    type: StoreTypes.Boolean
  },
  'geoLocate': {
    default: false,
    type: StoreTypes.Boolean
  },
  'lockMarker': {
    default: isTouchDevice(), // default to true if touch device
    type: StoreTypes.Boolean
  },
  'startAtUserLocation': {
    default: false,
    type: StoreTypes.Boolean
  },
  'pokemonIcons': {
    default: 'highres',
    type: StoreTypes.String
  },
  'iconSizeModifier': {
    default: 0,
    type: StoreTypes.Number
  },
  'searchMarkerStyle': {
    default: 'google',
    type: StoreTypes.String
  },
  'zoomLevel': {
    default: 16,
    type: StoreTypes.Number
  },
  'notify': {
    default: false,
    type: StoreTypes.Boolean
  },
  'select_notification_notify': {
    default: 'none',
    type: StoreTypes.String
  },
  'select_sound_notify': {
    default: 'none',
    type: StoreTypes.String
  },
  'select_audiosprite_notify': {
    default: 'default',
    type: StoreTypes.String
  },
  'select_texttospeech_notify': {
    default: 'none',
    type: StoreTypes.String
  },
  'select_nearby_notify': {
    default: [],
    type: StoreTypes.JSON
  },
  'select_nearbydistance_notify': {
    default: 1,
    type: StoreTypes.Number
  }
}

var Store = {
  getOption: function (key) {
    var option = StoreOptions[key]
    if (!option) {
      throw new Error('Store key was not defined ' + key)
    }
    return option
  },
  get: function (key) {
    var option = this.getOption(key)
    var optionType = option.type
    var rawValue = localStorage[key]
    if (rawValue === null || rawValue === undefined) {
      return option.default
    }
    var value = optionType.parse(rawValue)
    return value
  },
  set: function (key, value) {
    var option = this.getOption(key)
    var optionType = option.type || StoreTypes.String
    var rawValue = optionType.stringify(value)
    localStorage[key] = rawValue
  },
  reset: function (key) {
    localStorage.removeItem(key)
  }
}

//
// Functions
//

function excludePokemon (id) { // eslint-disable-line no-unused-vars
  $selectExclude.val(
    $selectExclude.val().concat(id)
  ).trigger('change')
}

function notifyAboutPokemon (id) { // eslint-disable-line no-unused-vars
  $selectPokemonNotify.val(
    $selectPokemonNotify.val().concat(id)
  ).trigger('change')
}

function removePokemonMarker (encounterId) { // eslint-disable-line no-unused-vars
  if (mapData.pokemons[encounterId].marker.rangeCircle) {
    mapData.pokemons[encounterId].marker.rangeCircle.setMap(null)
    delete mapData.pokemons[encounterId].marker.rangeCircle
  }
  mapData.pokemons[encounterId].marker.setMap(null)
  mapData.pokemons[encounterId].hidden = true
}

function initMap () { // eslint-disable-line no-unused-vars
  map = new google.maps.Map(document.getElementById('map'), {
    center: {
      lat: centerLat,
      lng: centerLng
    },
    zoom: Store.get('zoomLevel'),
    fullscreenControl: true,
    streetViewControl: false,
    mapTypeControl: false,
    mapTypeControlOptions: {
      style: google.maps.MapTypeControlStyle.DROPDOWN_MENU,
      position: google.maps.ControlPosition.RIGHT_TOP,
      mapTypeIds: [
        google.maps.MapTypeId.ROADMAP,
        google.maps.MapTypeId.SATELLITE,
        'nolabels_style',
        'dark_style',
        'style_light2',
        'style_pgo',
        'dark_style_nl',
        'style_light2_nl',
        'style_pgo_nl'
      ]
    }
  })

  var styleNoLabels = new google.maps.StyledMapType(noLabelsStyle, {
    name: 'No Labels'
  })
  map.mapTypes.set('nolabels_style', styleNoLabels)

  var styleDark = new google.maps.StyledMapType(darkStyle, {
    name: 'Dark'
  })
  map.mapTypes.set('dark_style', styleDark)

  var styleLight2 = new google.maps.StyledMapType(light2Style, {
    name: 'Light2'
  })
  map.mapTypes.set('style_light2', styleLight2)

  var stylePgo = new google.maps.StyledMapType(pGoStyle, {
    name: 'PokemonGo'
  })
  map.mapTypes.set('style_pgo', stylePgo)

  var styleDarkNl = new google.maps.StyledMapType(darkStyleNoLabels, {
    name: 'Dark (No Labels)'
  })
  map.mapTypes.set('dark_style_nl', styleDarkNl)

  var styleLight2Nl = new google.maps.StyledMapType(light2StyleNoLabels, {
    name: 'Light2 (No Labels)'
  })
  map.mapTypes.set('style_light2_nl', styleLight2Nl)

  var stylePgoNl = new google.maps.StyledMapType(pGoStyleNoLabels, {
    name: 'PokemonGo (No Labels)'
  })
  map.mapTypes.set('style_pgo_nl', stylePgoNl)

  map.addListener('maptypeid_changed', function (s) {
    Store.set('map_style', this.mapTypeId)
  })

  map.setMapTypeId(Store.get('map_style'))
  map.addListener('idle', updateMap)

  map.addListener('zoom_changed', function () {
    if (storeZoom === true) {
      Store.set('zoomLevel', this.getZoom())
    } else {
      storeZoom = true
    }

    redrawPokemon(mapData.pokemons)
    redrawPokemon(mapData.lurePokemons)
  })

  searchMarker = createSearchMarker()

  addMyLocationButton()
  initSidebar()
}

function updateSearchMarker (style) {
  if (style in searchMarkerStyles) {
    searchMarker.setIcon(searchMarkerStyles[style].icon)
    Store.set('searchMarkerStyle', style)
  }
  return searchMarker
}

function createSearchMarker () {
  var searchMarker = new google.maps.Marker({ // need to keep reference.
    position: {
      lat: centerLat,
      lng: centerLng
    },
    map: map,
    animation: google.maps.Animation.DROP,
    draggable: !Store.get('lockMarker'),
    icon: null,
    optimized: false,
    zIndex: google.maps.Marker.MAX_ZINDEX + 1
  })

  if (!searchMarker.rangeCircle && isRangeActive(map)) {
    searchMarker.rangeCircle = addRangeCircle(searchMarker, map, 'search')
  }
  var oldLocation = null
  google.maps.event.addListener(searchMarker, 'dragstart', function () {
    oldLocation = searchMarker.getPosition()
  })

  google.maps.event.addListener(searchMarker, 'dragend', function () {
    var newLocation = searchMarker.getPosition()
    changeSearchLocation(newLocation.lat(), newLocation.lng())
      .done(function () {
        oldLocation = null
        if (searchMarker.rangeCircle && Store.get('showRanges')) {
          searchMarker.rangeCircle.setCenter(newLocation)
        }
      })
      .fail(function () {
        if (oldLocation) {
          searchMarker.setPosition(oldLocation)
        }
      })
  })

  return searchMarker
}

var searchControlURI = 'search_control'
function searchControl (action) {
  $.post(searchControlURI + '?action=' + encodeURIComponent(action))
}
function updateSearchStatus () {
  $.getJSON(searchControlURI).then(function (data) {
    $('#search-switch').prop('checked', data.status)
  })
}

function initSidebar () {
  $('#gyms-switch').prop('checked', Store.get('showGyms'))
  $('#pokemon-switch').prop('checked', Store.get('showPokemon'))
  $('#pokestops-switch').prop('checked', Store.get('showPokestops'))
  $('#lured-pokestops-only-switch').val(Store.get('showLuredPokestopsOnly'))
  $('#lured-pokestops-only-wrapper').toggle(Store.get('showPokestops'))
  $('#geoloc-switch').prop('checked', Store.get('geoLocate'))
  $('#lock-marker-switch').prop('checked', Store.get('lockMarker'))
  $('#start-at-user-location-switch').prop('checked', Store.get('startAtUserLocation'))
  $('#scanned-switch').prop('checked', Store.get('showScanned'))
  $('#spawnpoints-switch').prop('checked', Store.get('showSpawnpoints'))
  $('#ranges-switch').prop('checked', Store.get('showRanges'))
  $('#notify-switch').prop('checked', Store.get('notify'))
  var searchBox = new google.maps.places.SearchBox(document.getElementById('next-location'))
  $('#next-location').css('background-color', $('#geoloc-switch').prop('checked') ? '#e0e0e0' : '#ffffff')

  updateSearchStatus()
  setInterval(updateSearchStatus, 5000)

  searchBox.addListener('places_changed', function () {
    var places = searchBox.getPlaces()

    if (places.length === 0) {
      return
    }

    var loc = places[0].geometry.location
    changeLocation(loc.lat(), loc.lng())
  })

  var icons = $('#pokemon-icons')
  $.each(pokemonSprites, function (key, value) {
    icons.append($('<option></option>').attr('value', key).text(value.name))
  })
  icons.val((pokemonSprites[Store.get('pokemonIcons')]) ? Store.get('pokemonIcons') : 'highres')
  $('#pokemon-icon-size').val(Store.get('iconSizeModifier'))
}

function pad (number) {
  return number <= 99 ? ('0' + number).slice(-2) : number
}

function getTypeSpan (type) {
  return `<span style='padding: 2px 5px; text-transform: uppercase; color: white; margin-right: 2px; border-radius: 4px; font-size: 0.8em; vertical-align: text-bottom; background-color: ${type['color']}'>${type['type']}</span>`
}

function pokemonLabel (name, rarity, types, disappearTime, id, latitude, longitude, encounterId) {
  var disappearDate = new Date(disappearTime)
  var rarityDisplay = rarity ? '(' + rarity + ')' : ''
  var typesDisplay = ''
  $.each(types, function (index, type) {
    typesDisplay += getTypeSpan(type)
  })

  var contentstring = `
    <div>
      <b>${name}</b>
      <span> - </span>
      <small>
        <a href='http://www.pokemon.com/us/pokedex/${id}' target='_blank' title='View in Pokedex'>#${id}</a>
      </small>
      <span> ${rarityDisplay}</span>
      <span> - </span>
      <small>${typesDisplay}</small>
    </div>
    <div>
      Disappears at ${pad(disappearDate.getHours())}:${pad(disappearDate.getMinutes())}:${pad(disappearDate.getSeconds())}
      <span class='label-countdown' disappears-at='${disappearTime}'>(00m00s)</span>
    </div>
    <div>
      Location: ${latitude.toFixed(6)}, ${longitude.toFixed(7)}
    </div>
    <div>
      <a href='javascript:excludePokemon(${id})'>Exclude</a>&nbsp;&nbsp
      <a href='javascript:notifyAboutPokemon(${id})'>Notify</a>&nbsp;&nbsp
      <a href='javascript:removePokemonMarker("${encounterId}")'>Remove</a>&nbsp;&nbsp
      <a href='https://www.google.com/maps/dir/Current+Location/${latitude},${longitude}?hl=en' target='_blank' title='View in Maps'>Get directions</a>
    </div>`
  return contentstring
}

function gymLabel (teamName, teamId, gymPoints, latitude, longitude, lastScanned = null, name = null, members = []) {
  var memberStr = ''
  for (var i = 0; i < members.length; i++) {
    memberStr += `
      <span class="gym-member" title="${members[i].pokemon_name} | ${members[i].trainer_name} (Lvl ${members[i].trainer_level})">
        <i class="pokemon-sprite n${members[i].pokemon_id}"></i>
        <span class="cp team-${teamId}">${members[i].pokemon_cp}</span>
      </span>`
  }

  var lastScannedStr
  if (lastScanned) {
    var lastScannedDate = new Date(lastScanned)
    lastScannedStr = `${lastScannedDate.getFullYear()}-${pad(lastScannedDate.getMonth() + 1)}-${lastScannedDate.getDate()} ${pad(lastScannedDate.getHours())}:${pad(lastScannedDate.getMinutes())}:${pad(lastScannedDate.getSeconds())}`
  } else {
    lastScannedStr = 'Unknown'
  }

  var nameStr = (name ? `<div>${name}</div>` : '')

  var gymColor = ['0, 0, 0, .4', '74, 138, 202, .6', '240, 68, 58, .6', '254, 217, 40, .6']
  var str
  if (teamId === 0) {
    str = `
      <div>
        <center>
          <div>
            <b style='color:rgba(${gymColor[teamId]})'>${teamName}</b><br>
            <img height='70px' style='padding: 5px;' src='static/forts/${teamName}_large.png'>
          </div>
          ${nameStr}
          <div>
            Location: ${latitude.toFixed(6)}, ${longitude.toFixed(7)}
          </div>
          <div>
            Last Scanned: ${lastScannedStr}
          </div>
          <div>
            <a href='https://www.google.com/maps/dir/Current+Location/${latitude},${longitude}?hl=en' target='_blank' title='View in Maps'>Get directions</a>
          </div>
        </center>
      </div>`
  } else {
    var gymPrestige = [2000, 4000, 8000, 12000, 16000, 20000, 30000, 40000, 50000]
    var gymLevel = 1
    while (gymPoints >= gymPrestige[gymLevel - 1]) {
      gymLevel++
    }
    str = `
      <div>
        <center>
          <div style='padding-bottom: 2px'>
            Gym owned by:
          </div>
          <div>
            <b style='color:rgba(${gymColor[teamId]})'>Team ${teamName}</b><br>
            <img height='70px' style='padding: 5px;' src='static/forts/${teamName}_large.png'>
          </div>
          <div>
            ${nameStr}
          </div>
          <div>
            Level: ${gymLevel} | Prestige: ${gymPoints}/${gymPrestige[gymLevel - 1] || 50000}
          </div>
          <div>
            ${memberStr}
          </div>
          <div>
            Location: ${latitude.toFixed(6)}, ${longitude.toFixed(7)}
          </div>
          <div>
            Last Scanned: ${lastScannedStr}
          </div>
          <div>
            <a href='https://www.google.com/maps/dir/Current+Location/${latitude},${longitude}?hl=en' target='_blank' title='View in Maps'>Get directions</a>
          </div>
        </center>
      </div>`
  }

  return str
}

function pokestopLabel (expireTime, latitude, longitude) {
  var str
  if (expireTime) {
    var expireDate = new Date(expireTime)

    str = `
      <div>
        <b>Lured Pokéstop</b>
      </div>
      <div>
        Lure expires at ${pad(expireDate.getHours())}:${pad(expireDate.getMinutes())}:${pad(expireDate.getSeconds())}
        <span class='label-countdown' disappears-at='${expireTime}'>(00m00s)</span>
      </div>
      <div>
        Location: ${latitude.toFixed(6)}, ${longitude.toFixed(7)}
      </div>
      <div>
        <a href='https://www.google.com/maps/dir/Current+Location/${latitude},${longitude}?hl=en' target='_blank' title='View in Maps'>Get directions</a>
      </div>`
  } else {
    str = `
      <div>
        <b>Pokéstop</b>
      </div>
      <div>
        Location: ${latitude.toFixed(6)}, ${longitude.toFixed(7)}
      </div>
      <div>
        <a href='https://www.google.com/maps/dir/Current+Location/${latitude},${longitude}?hl=en' target='_blank' title='View in Maps'>Get directions</a>
      </div>`
  }

  return str
}

function getGoogleSprite (index, sprite, displayHeight) {
  displayHeight = Math.max(displayHeight, 3)
  var scale = displayHeight / sprite.iconHeight
  // Crop icon just a tiny bit to avoid bleedover from neighbor
  var scaledIconSize = new google.maps.Size(scale * sprite.iconWidth - 1, scale * sprite.iconHeight - 1)
  var scaledIconOffset = new google.maps.Point(
    (index % sprite.columns) * sprite.iconWidth * scale + 0.5,
    Math.floor(index / sprite.columns) * sprite.iconHeight * scale + 0.5)
  var scaledSpriteSize = new google.maps.Size(scale * sprite.spriteWidth, scale * sprite.spriteHeight)
  var scaledIconCenterOffset = new google.maps.Point(scale * sprite.iconWidth / 2, scale * sprite.iconHeight / 2)

  return {
    url: sprite.filename,
    size: scaledIconSize,
    scaledSize: scaledSpriteSize,
    origin: scaledIconOffset,
    anchor: scaledIconCenterOffset
  }
}

function addRangeCircle (marker, map, type, teamId) {
  var targetmap = null
  var circleCenter = new google.maps.LatLng(marker.position.lat(), marker.position.lng())
  var gymColors = ['#999999', '#0051CF', '#FF260E', '#FECC23'] // 'Uncontested', 'Mystic', 'Valor', 'Instinct']
  var circleColor = '#cccccc'
  var teamColor = gymColors[0]
  if (teamId) teamColor = gymColors[teamId]

  if (type === 'search') circleColor = '#333333'
  if (type === 'pokemon') circleColor = '#C233F2'
  if (type === 'pokestop') circleColor = '#3EB0FF'
  if (type === 'gym') circleColor = teamColor

  if (map) targetmap = map

  var rangeCircleOpts = {
    map: targetmap,
    radius: 40,    // 40 meters
    strokeWeight: 1,
    strokeColor: circleColor,
    strokeOpacity: 0.9,
    center: circleCenter,
    fillColor: circleColor,
    fillOpacity: 0.3
  }
  var rangeCircle = new google.maps.Circle(rangeCircleOpts)
  return rangeCircle
}

function isRangeActive (map) {
  if (map.getZoom() < 16) return false
  return Store.get('showRanges')
}

function setupPokemonMarker (item, skipNotification, isBounceDisabled) {
  // Scale icon size up with the map exponentially
  var iconSize = 2 + (map.getZoom() - 3) * (map.getZoom() - 3) * 0.2 + Store.get('iconSizeModifier')
  var pokemonIndex = item['pokemon_id'] - 1
  var sprite = pokemonSprites[Store.get('pokemonIcons')] || pokemonSprites['highres']
  var icon = getGoogleSprite(pokemonIndex, sprite, iconSize)

  var animationDisabled = false
  if (isBounceDisabled === true) {
    animationDisabled = true
  }

  var marker = new google.maps.Marker({
    position: {
      lat: item['latitude'],
      lng: item['longitude']
    },
    zIndex: 9999,
    map: map,
    icon: icon,
    animationDisabled: animationDisabled
  })

  marker.addListener('click', function () {
    this.setAnimation(null)
    this.animationDisabled = true
  })

  if (!marker.rangeCircle && isRangeActive(map)) {
    marker.rangeCircle = addRangeCircle(marker, map, 'pokemon')
  }

  marker.infoWindow = new google.maps.InfoWindow({
    content: pokemonLabel(item['pokemon_name'], item['pokemon_rarity'], item['pokemon_types'], item['disappear_time'], item['pokemon_id'], item['latitude'], item['longitude'], item['encounter_id']),
    disableAutoPan: true
  })

  if (notifiedPokemon.indexOf(item['pokemon_id']) > -1 || notifiedRarity.indexOf(item['pokemon_rarity']) > -1) {
    if (Store.get('notify')) {
      processNotifications(item, marker, skipNotification)
    }
  }

  addListeners(marker)
  return marker
}

function setupGymMarker (item) {
  var marker = new google.maps.Marker({
    position: {
      lat: item['latitude'],
      lng: item['longitude']
    },
    map: map,
    icon: 'static/forts/' + gymTypes[item['team_id']] + '.png'
  })

  if (!marker.rangeCircle && isRangeActive(map)) {
    marker.rangeCircle = addRangeCircle(marker, map, 'gym', item['team_id'])
  }

  marker.infoWindow = new google.maps.InfoWindow({
    content: gymLabel(gymTypes[item['team_id']], item['team_id'], item['gym_points'], item['latitude'], item['longitude'], item['last_scanned'], item['name'], item['pokemon']),
    disableAutoPan: true
  })

  addListeners(marker)
  return marker
}

function updateGymMarker (item, marker) {
  marker.setIcon('static/forts/' + gymTypes[item['team_id']] + '.png')
  marker.infoWindow.setContent(gymLabel(gymTypes[item['team_id']], item['team_id'], item['gym_points'], item['latitude'], item['longitude'], item['last_scanned'], item['name'], item['pokemon']))
  return marker
}

function setupPokestopMarker (item) {
  var imagename = item['lure_expiration'] ? 'PstopLured' : 'Pstop'
  var marker = new google.maps.Marker({
    position: {
      lat: item['latitude'],
      lng: item['longitude']
    },
    map: map,
    zIndex: 2,
    icon: 'static/forts/' + imagename + '.png'
  })

  if (!marker.rangeCircle && isRangeActive(map)) {
    marker.rangeCircle = addRangeCircle(marker, map, 'pokestop')
  }

  marker.infoWindow = new google.maps.InfoWindow({
    content: pokestopLabel(item['lure_expiration'], item['latitude'], item['longitude']),
    disableAutoPan: true
  })

  addListeners(marker)
  return marker
}

function getColorByDate (value) {
  // Changes the color from red to green over 15 mins
  var diff = (Date.now() - value) / 1000 / 60 / 15

  if (diff > 1) {
    diff = 1
  }

  // value from 0 to 1 - Green to Red
  var hue = ((1 - diff) * 120).toString(10)
  return ['hsl(', hue, ',100%,50%)'].join('')
}

function setupScannedMarker (item) {
  var circleCenter = new google.maps.LatLng(item['latitude'], item['longitude'])

  var marker = new google.maps.Circle({
    map: map,
    clickable: false,
    center: circleCenter,
    radius: 70, // metres
    fillColor: getColorByDate(item['last_modified']),
    fillOpacity: 0.1,
    strokeWeight: 1,
    strokeOpacity: 0.5
  })

  return marker
}

function setupSpawnpointMarker (item) {
  var circleCenter = new google.maps.LatLng(item['latitude'], item['longitude'])

  var marker = new google.maps.Circle({
    map: map,
    clickable: false,
    center: circleCenter,
    radius: 5, // metres
    fillColor: 'blue',
    strokeWeight: 1
  })

  return marker
}

function clearSelection () {
  if (document.selection) {
    document.selection.empty()
  } else if (window.getSelection) {
    window.getSelection().removeAllRanges()
  }
}

function addListeners (marker) {
  marker.addListener('click', function () {
    marker.infoWindow.open(map, marker)
    clearSelection()
    updateLabelDiffTime()
    marker.persist = true
  })

  google.maps.event.addListener(marker.infoWindow, 'closeclick', function () {
    marker.persist = null
  })

  marker.addListener('mouseover', function () {
    marker.infoWindow.open(map, marker)
    clearSelection()
    updateLabelDiffTime()
  })

  marker.addListener('mouseout', function () {
    if (!marker.persist) {
      marker.infoWindow.close()
    }
  })

  return marker
}

function clearStaleMarkers () {
  $.each(mapData.pokemons, function (key, value) {
    if (mapData.pokemons[key]['disappear_time'] < new Date().getTime() ||
      excludedPokemon.indexOf(mapData.pokemons[key]['pokemon_id']) >= 0) {
      if (mapData.pokemons[key].marker.rangeCircle) {
        mapData.pokemons[key].marker.rangeCircle.setMap(null)
        delete mapData.pokemons[key].marker.rangeCircle
      }
      mapData.pokemons[key].marker.setMap(null)
      delete mapData.pokemons[key]
    }
  })

  $.each(mapData.lurePokemons, function (key, value) {
    if (mapData.lurePokemons[key]['lure_expiration'] < new Date().getTime() ||
      excludedPokemon.indexOf(mapData.lurePokemons[key]['pokemon_id']) >= 0) {
      mapData.lurePokemons[key].marker.setMap(null)
      delete mapData.lurePokemons[key]
    }
  })

  $.each(mapData.scanned, function (key, value) {
    // If older than 15mins remove
    if (mapData.scanned[key]['last_modified'] < (new Date().getTime() - 15 * 60 * 1000)) {
      mapData.scanned[key].marker.setMap(null)
      delete mapData.scanned[key]
    }
  })
}

function showInBoundsMarkers (markers, type) {
  $.each(markers, function (key, value) {
    var marker = markers[key].marker
    var show = false
    if (!markers[key].hidden) {
      if (typeof marker.getBounds === 'function') {
        if (map.getBounds().intersects(marker.getBounds())) {
          show = true
        }
      } else if (typeof marker.getPosition === 'function') {
        if (map.getBounds().contains(marker.getPosition())) {
          show = true
        }
      }
    }
    // marker has an associated range
    if (show && rangeMarkers.indexOf(type) !== -1) {
      // no range circle yet...let's create one
      if (!marker.rangeCircle) {
        // but only if range is active
        if (isRangeActive(map)) {
          if (type === 'gym') marker.rangeCircle = addRangeCircle(marker, map, type, markers[key].team_id)
          else marker.rangeCircle = addRangeCircle(marker, map, type)
        }
      } else { // there's already a range circle
        if (isRangeActive(map)) {
          marker.rangeCircle.setMap(map)
        } else {
          marker.rangeCircle.setMap(null)
        }
      }
    }

    if (show && !marker.getMap()) {
      marker.setMap(map)
      // Not all markers can be animated (ex: scan locations)
      if (marker.setAnimation && marker.oldAnimation) {
        marker.setAnimation(marker.oldAnimation)
      }
    } else if (!show && marker.getMap()) {
      // Not all markers can be animated (ex: scan locations)
      if (marker.getAnimation) {
        marker.oldAnimation = marker.getAnimation()
      }
      if (marker.rangeCircle) marker.rangeCircle.setMap(null)
      marker.setMap(null)
    }
  })
}

function loadRawData () {
  var loadPokemon = Store.get('showPokemon')
  var loadGyms = Store.get('showGyms')
  var loadPokestops = Store.get('showPokestops')
  var loadScanned = Store.get('showScanned')
  var loadSpawnpoints = Store.get('showSpawnpoints')

  var bounds = map.getBounds()
  var swPoint = bounds.getSouthWest()
  var nePoint = bounds.getNorthEast()
  var swLat = swPoint.lat()
  var swLng = swPoint.lng()
  var neLat = nePoint.lat()
  var neLng = nePoint.lng()

  return $.ajax({
    url: 'raw_data',
    type: 'GET',
    data: {
      'pokemon': loadPokemon,
      'pokestops': loadPokestops,
      'gyms': loadGyms,
      'scanned': loadScanned,
      'spawnpoints': loadSpawnpoints,
      'swLat': swLat,
      'swLng': swLng,
      'neLat': neLat,
      'neLng': neLng
    },
    dataType: 'json',
    cache: false,
    beforeSend: function () {
      if (rawDataIsLoading) {
        return false
      } else {
        rawDataIsLoading = true
      }
    },
    complete: function () {
      rawDataIsLoading = false
    }
  })
}

function processPokemons (i, item) {
  if (!Store.get('showPokemon')) {
    return false // in case the checkbox was unchecked in the meantime.
  }

  if (!(item['encounter_id'] in mapData.pokemons) &&
    excludedPokemon.indexOf(item['pokemon_id']) < 0) {
    // add marker to map and item to dict
    if (item.marker) {
      item.marker.setMap(null)
    }
    if (!item.hidden) {
      item.marker = setupPokemonMarker(item)
      mapData.pokemons[item['encounter_id']] = item
    }
  }
}

function processPokestops (i, item) {
  if (!Store.get('showPokestops')) {
    return false
  }

  if (Store.get('showLuredPokestopsOnly') && !item['lure_expiration']) {
    if (mapData.pokestops[item['pokestop_id']] && mapData.pokestops[item['pokestop_id']].marker) {
      if (mapData.pokestops[item['pokestop_id']].marker.rangeCircle) {
        mapData.pokestops[item['pokestop_id']].marker.rangeCircle.setMap(null)
      }
      mapData.pokestops[item['pokestop_id']].marker.setMap(null)
      delete mapData.pokestops[item['pokestop_id']]
    }
    return true
  }

  if (!mapData.pokestops[item['pokestop_id']]) { // add marker to map and item to dict
    // add marker to map and item to dict
    if (item.marker && item.marker.rangeCircle) {
      item.marker.rangeCircle.setMap(null)
    }
    if (item.marker) {
      item.marker.setMap(null)
    }
    item.marker = setupPokestopMarker(item)
    mapData.pokestops[item['pokestop_id']] = item
  } else {
    var item2 = mapData.pokestops[item['pokestop_id']]
    if (!!item['lure_expiration'] !== !!item2['lure_expiration']) {
      if (item2.marker && item2.marker.rangeCircle) {
        item2.marker.rangeCircle.setMap(null)
      }
      item2.marker.setMap(null)
      item.marker = setupPokestopMarker(item)
      mapData.pokestops[item['pokestop_id']] = item
    }
  }
}

function processGyms (i, item) {
  if (!Store.get('showGyms')) {
    return false // in case the checkbox was unchecked in the meantime.
  }

  if (item['gym_id'] in mapData.gyms) {
    item.marker = updateGymMarker(item, mapData.gyms[item['gym_id']].marker)
  } else { // add marker to map and item to dict
    item.marker = setupGymMarker(item)
  }
  mapData.gyms[item['gym_id']] = item
}

function processScanned (i, item) {
  if (!Store.get('showScanned')) {
    return false
  }

  var scanId = item['latitude'] + '|' + item['longitude']

  if (scanId in mapData.scanned) {
    mapData.scanned[scanId].marker.setOptions({
      fillColor: getColorByDate(item['last_modified'])
    })
  } else { // add marker to map and item to dict
    if (item.marker) {
      item.marker.setMap(null)
    }
    item.marker = setupScannedMarker(item)
    mapData.scanned[scanId] = item
  }
}

function processSpawnpoints (i, item) {
  if (!Store.get('showSpawnpoints')) {
    return false
  }

  var id = item['spawnpoint_id']

  if (id in mapData.spawnpoints) {
    // In the future: maybe show how long till spawnpoint activates?
  } else { // add marker to map and item to dict
    if (item.marker) {
      item.marker.setMap(null)
    }
    item.marker = setupSpawnpointMarker(item)
    mapData.spawnpoints[id] = item
  }
}

function updateMap () {
  loadRawData().done(function (result) {
    $.each(result.pokemons, processPokemons)
    $.each(result.pokestops, processPokestops)
    $.each(result.gyms, processGyms)
    $.each(result.scanned, processScanned)
    $.each(result.spawnpoints, processSpawnpoints)
    showInBoundsMarkers(mapData.pokemons, 'pokemon')
    showInBoundsMarkers(mapData.lurePokemons, 'pokemon')
    showInBoundsMarkers(mapData.gyms, 'gym')
    showInBoundsMarkers(mapData.pokestops, 'pokestop')
    showInBoundsMarkers(mapData.scanned, 'scanned')
    showInBoundsMarkers(mapData.spawnpoints, 'inbound')
    clearStaleMarkers()
    if ($('#stats').hasClass('visible')) {
      countMarkers()
    }
  })
}

function redrawPokemon (pokemonList) {
  var skipNotification = true
  $.each(pokemonList, function (key, value) {
    var item = pokemonList[key]
    if (!item.hidden) {
      if (item.marker.rangeCircle) item.marker.rangeCircle.setMap(null)
      var newMarker = setupPokemonMarker(item, skipNotification, this.marker.animationDisabled)
      item.marker.setMap(null)
      pokemonList[key].marker = newMarker
    }
  })
}

var updateLabelDiffTime = function () {
  $('.label-countdown').each(function (index, element) {
    var disappearsAt = new Date(parseInt(element.getAttribute('disappears-at')))
    var now = new Date()

    var difference = Math.abs(disappearsAt - now)
    var hours = Math.floor(difference / 36e5)
    var minutes = Math.floor((difference - (hours * 36e5)) / 6e4)
    var seconds = Math.floor((difference - (hours * 36e5) - (minutes * 6e4)) / 1e3)
    var timestring = ''

    if (disappearsAt < now) {
      timestring = '(expired)'
    } else {
      timestring = '('
      if (hours > 0) {
        timestring = hours + 'h'
      }

      timestring += ('0' + minutes).slice(-2) + 'm'
      timestring += ('0' + seconds).slice(-2) + 's'
      timestring += ')'
    }

    $(element).text(timestring)
  })
}

function getPointDistance (pointA, pointB) {
  return google.maps.geometry.spherical.computeDistanceBetween(pointA, pointB)
}

function getPokemonDistance (item) {
  if (!(locationMarker)) {
    return 0
  }
  return parseInt(google.maps.geometry.spherical.computeDistanceBetween(locationMarker.getPosition(), new google.maps.LatLng(item.latitude, item.longitude)))
}

function getPokemonHeading (item) {
  if (!(locationMarker)) {
    return 0
  }
  return google.maps.geometry.spherical.computeHeading(locationMarker.getPosition(), new google.maps.LatLng(item.latitude, item.longitude))
}

function getHeadingOrdinal (heading) {
  if ((heading >= -22 && heading <= 22)) {
    return i8ln('North')
  } else if (heading >= 68 && heading <= 112) {
    return i8ln('East')
  } else if ((heading >= -180 && heading <= -158) || (heading >= 158 && heading <= 180)) {
    return i8ln('South')
  } else if (heading >= -112 && heading <= -68) {
    return i8ln('West')
  } else if (heading > 0 && heading < 90) {
    return i8ln('North East')
  } else if (heading > 90 && heading < 180) {
    return i8ln('South East')
  } else if (heading > -90 && heading < 0) {
    return i8ln('North West')
  } else if (heading > -180 && heading < -90) {
    return i8ln('South West')
  }
}

function processNotifications (item, marker, refresh) {
  function _shouldNotify (storeKey, distance) {
    // has notification distance JSON finished loading?
    if (!(Store.get(storeKey) in notificationDistances)) {
      return false
    }
    var distanceItem = notificationDistances[Store.get(storeKey)]
    if (!(distanceItem.type === 'none') && (distanceItem.type === 'all' || distanceItem.type === 'less' && distance <= parseInt(distanceItem.value) || distanceItem.type === 'more' && distance > parseInt(distanceItem.value))) {
      return true
    }
    return false
  }

  if (!refresh) {
    var notificationTitle
    var notitifcationMessage
    var pokemonDistance = getPokemonDistance(item)
    var pokemonOrdinal = getHeadingOrdinal(getPokemonHeading(item))
    var pokemonId = item.pokemon_id.toString()
    var isNearBy = (pokemonDistance <= parseInt(Store.get('select_nearbydistance_notify')))
    var nearByNotify = Store.get('select_nearby_notify')

    var pokemonRarityId = {
      [i8ln('Common')]: '1',
      [i8ln('Uncommon')]: '2',
      [i8ln('Rare')]: '3',
      [i8ln('Very Rare')]: '4',
      [i8ln('Ultra Rare')]: '5'
    }[item.pokemon_rarity]

    pushNotify.nextNotifyTime = soundNotify.nextNotifyTime = textToSpeechNotify.nextNotifyTime = Math.max.apply(null, [pushNotify.nextNotifyTime, soundNotify.nextNotifyTime, textToSpeechNotify.nextNotifyTime])

    // Throttle notifications to < 1 min, notification maxQueue's are also set at 5 (no more than 5 notifications queued)
    if (pushNotify.nextNotifyTime - Date.now() > 60000) {
      return
    }

    if (isNearBy && nearByNotify.indexOf(1) >= 0) {
      notificationTitle = 'A nearby wild ' + item.pokemon_rarity + ' ' + item.pokemon_name + ' appeared!'
      notitifcationMessage = pokemonDistance + ' ' + i8ln('Meters') + ' ' + pokemonOrdinal + ' (Click to load map)'
      pushNotify.notify(notificationTitle, notitifcationMessage, 'static/icons/' + pokemonId + '.png', item.latitude, item.longitude)
    } else if (_shouldNotify('select_notification_notify', pokemonDistance)) {
      notificationTitle = 'A wild ' + item.pokemon_rarity + ' ' + item.pokemon_name + ' appeared!'
      notitifcationMessage = pokemonDistance + ' ' + i8ln('Meters') + ' ' + pokemonOrdinal + ' (Click to load map)'
      pushNotify.notify(notificationTitle, notitifcationMessage, 'static/icons/' + pokemonId + '.png', item.latitude, item.longitude)
    }

    if (isNearBy && nearByNotify.indexOf(2) >= 0) {
      if (!soundNotify.notify(pokemonId + '-nearby')) {
        if (!soundNotify.notify('default-nearby')) {
          if (!soundNotify.notify('rarity-' + pokemonRarityId)) {
            soundNotify.notify('default')
          }
        }
      }
      if (!soundNotify.notify(pokemonId)) {
        if (!soundNotify.notify('rarity-' + pokemonRarityId)) {
          soundNotify.notify('default')
        }
      }
    } else if (_shouldNotify('select_sound_notify', pokemonDistance)) {
      if (!soundNotify.notify(pokemonId)) {
        if (!soundNotify.notify('rarity-' + pokemonRarityId)) {
          soundNotify.notify('default')
        }
      }
    }

    if (isNearBy && nearByNotify.indexOf(3) >= 0) {
      textToSpeechNotify.notify(i8ln('Nearby') + item.pokemon_rarity + ' ' + item.pokemon_name + '. ' + pokemonDistance + ' ' + i8ln('Meters') + ' ' + pokemonOrdinal, soundNotify.nextNotifyTime)
    } else if (_shouldNotify('select_texttospeech_notify', pokemonDistance)) {
      textToSpeechNotify.notify(item.pokemon_rarity + ' ' + item.pokemon_name + '. ' + pokemonDistance + ' ' + i8ln('Meters') + ' ' + pokemonOrdinal, soundNotify.nextNotifyTime)
    }
  }

  if (marker.animationDisabled !== true) {
    marker.setAnimation(google.maps.Animation.BOUNCE)
  }
}

function SoundNotification (queueMax) {
  this.nextNotifyTime = 0
  this.minInterval = 500
  this.queueMax = queueMax
  this.queueCurrent = 0

  this.notify = function (soundId, notifyTime) {
    if ((soundId in createjs.Sound._idHash) && createjs.Sound.loadComplete(soundId)) {
      if (this.queueCurrent >= this.queueMax) {
        return true // we could indicate we are suppressing
      }
      this.queueCurrent += 1
      var delay = Math.max(0, (notifyTime || this.nextNotifyTime) - Date.now())
      var audioInstance = createjs.Sound.play(soundId, new createjs.PlayPropsConfig().set({delay: delay}))
      audioInstance.on('complete', () => { this.queueCurrent -= 1 })
      audioInstance.on('failed', () => { this.queueCurrent -= 1 })
      this.nextNotifyTime = Date.now() + audioInstance.duration + this.minInterval + delay
      return true
    }
    return false
  }

  this.load = function (source, path) {
    createjs.Sound.removeAllSounds()

    if (!createjs.Sound.hasEventListener('fileload')) {
      createjs.Sound.on('fileload', _fileLoaded)
    }
    if (!createjs.Sound.hasEventListener('fileerror')) {
      createjs.Sound.on('fileerror', _fileError)
    }

    $.getJSON(source).done(function (data) {
      createjs.Sound.registerSounds(data, path)
    })
  }

  function _fileLoaded (event) {

  }

  function _fileError (event) {
    console.log('Sound file Error: ', event.id, event.src)
  }
}

function PushNotification (queueMax) {
  this.nextNotifyTime = 0
  this.minInterval = 500
  this.queueMax = queueMax
  this.queueCurrent = 0

  this.notify = function (title, text, icon, lat, lng, notifyTime) {
    if (Push.isSupported) {
      if (this.queueCurrent >= this.queueMax) {
        return // we could indicate we are suppressing
      }
      this.queueCurrent += 1
      var delay = Math.max(0, (notifyTime || this.nextNotifyTime) - Date.now())
      this.nextNotifyTime = Date.now() + this.minInterval + delay
      setTimeout(() => {
        this.queueCurrent -= 1
        _notify(title, text, icon, lat, lng)
      }, delay)
    }
  }

  function _notify (title, text, icon, lat, lng) {
    Push.create(title, {
      icon: icon,
      body: text,
      timeout: 5000,
      data: {
        url: location.protocol + '//' + location.host + location.pathname + '?centermap=' + lat + ',' + lng,
        lat: lat,
        lng: lng
      },
      onClick: function () {
        window.focus()
        this.close()
        centerMap(lat, lng, 20)
      },
      vibrate: [300, 100, 300]
    })
  }
}

function TextToSpeechNotification (queueMax) {
  this.nextNotifyTime = 0
  this.minInterval = 5000 // max time per phrase
  this.queueMax = queueMax
  this.queueCurrent = 0

  this.iOS = (/iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream)
  this.iOSInitialized = false
  this.clickEventInitialized = false

  this.clickEvent = function () {
    if (this.iOS && !this.clickEventInitialized) {
      var utterance = new SpeechSynthesisUtterance(' ')
      window.speechSynthesis.speak(utterance)
      this.clickEventInitialized = true
    }
  }

  this.notify = function (phrase, notifyTime) {
    if ('speechSynthesis' in window) {
      if (this.iOS && !this.iOSInitialized) {
        setTimeout(() => {
          this.notify(phrase, notifyTime)
        }
        , 100)
        this.clickEvent()
        this.iOSInitialized = true
      } else {
        if (this.queueCurrent >= this.queueMax) {
          return // we could indicate we are suppressing
        }
        this.queueCurrent += 1
        var delay = Math.max(0, (notifyTime || this.nextNotifyTime) - Date.now())
        this.nextNotifyTime = Date.now() + this.minInterval + delay
        setTimeout(() => {
          this.queueCurrent -= 1
          var utterance = new SpeechSynthesisUtterance(phrase)
          utterance.rate = 0.8
          utterance.lang = language
          window.speechSynthesis.speak(utterance)
        }, delay)
      }
    }
  }
}

function myLocationButton (map, marker) {
  var locationContainer = document.createElement('div')

  var locationButton = document.createElement('button')
  locationButton.style.backgroundColor = '#fff'
  locationButton.style.border = 'none'
  locationButton.style.outline = 'none'
  locationButton.style.width = '28px'
  locationButton.style.height = '28px'
  locationButton.style.borderRadius = '2px'
  locationButton.style.boxShadow = '0 1px 4px rgba(0,0,0,0.3)'
  locationButton.style.cursor = 'pointer'
  locationButton.style.marginRight = '10px'
  locationButton.style.padding = '0px'
  locationButton.title = 'Your Location'
  locationContainer.appendChild(locationButton)

  var locationIcon = document.createElement('div')
  locationIcon.style.margin = '5px'
  locationIcon.style.width = '18px'
  locationIcon.style.height = '18px'
  locationIcon.style.backgroundImage = 'url(static/mylocation-sprite-1x.png)'
  locationIcon.style.backgroundSize = '180px 18px'
  locationIcon.style.backgroundPosition = '0px 0px'
  locationIcon.style.backgroundRepeat = 'no-repeat'
  locationIcon.id = 'current-location'
  locationButton.appendChild(locationIcon)

  locationButton.addEventListener('click', function () {
    centerMapOnLocation()
  })

  locationContainer.index = 1
  map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(locationContainer)
}

function centerMapOnLocation () {
  var currentLocation = document.getElementById('current-location')
  var imgX = '0'
  var animationInterval = setInterval(function () {
    if (imgX === '-18') {
      imgX = '0'
    } else {
      imgX = '-18'
    }
    currentLocation.style.backgroundPosition = imgX + 'px 0'
  }, 500)
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function (position) {
      var latlng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude)
      locationMarker.setVisible(true)
      locationMarker.setOptions({
        'opacity': 1
      })
      locationMarker.setPosition(latlng)
      map.setCenter(latlng)
      clearInterval(animationInterval)
      currentLocation.style.backgroundPosition = '-144px 0px'
    })
  } else {
    clearInterval(animationInterval)
    currentLocation.style.backgroundPosition = '0px 0px'
  }
}

function addMyLocationButton () {
  locationMarker = new google.maps.Marker({
    map: map,
    animation: google.maps.Animation.DROP,
    position: {
      lat: centerLat,
      lng: centerLng
    },
    icon: {
      path: google.maps.SymbolPath.CIRCLE,
      fillOpacity: 1,
      fillColor: '#1c8af6',
      scale: 6,
      strokeColor: '#1c8af6',
      strokeWeight: 8,
      strokeOpacity: 0.3
    }
  })
  locationMarker.setVisible(false)

  myLocationButton(map, locationMarker)

  google.maps.event.addListener(map, 'dragend', function () {
    var currentLocation = document.getElementById('current-location')
    currentLocation.style.backgroundPosition = '0px 0px'
    locationMarker.setOptions({
      'opacity': 0.5
    })
  })
}

function changeLocation (lat, lng) {
  var loc = new google.maps.LatLng(lat, lng)
  changeSearchLocation(lat, lng).done(function () {
    map.setCenter(loc)
    searchMarker.setPosition(loc)
    if (searchMarker.rangeCircle) searchMarker.rangeCircle.setCenter(loc)
  })
}

function changeSearchLocation (lat, lng) {
  return $.post('next_loc?lat=' + lat + '&lon=' + lng, {})
}

function centerMap (lat, lng, zoom) {
  var loc = new google.maps.LatLng(lat, lng)

  map.setCenter(loc)

  if (zoom) {
    storeZoom = false
    map.setZoom(zoom)
  }
}

function i8ln (word) {
  if ($.isEmptyObject(i8lnDictionary) && language !== 'en' && languageLookups < languageLookupThreshold) {
    $.ajax({
      url: 'static/dist/locales/' + language + '.min.json',
      dataType: 'json',
      async: false,
      success: function (data) {
        i8lnDictionary = data
      },
      error: function (jqXHR, status, error) {
        console.log('Error loading i8ln dictionary: ' + error)
        languageLookups++
      }
    })
  }
  if (word in i8lnDictionary) {
    return i8lnDictionary[word]
  } else {
    // Word doesn't exist in dictionary return it as is
    return word
  }
}

// Replace the phrases in a sentence that are enclosed in { } with i8ln
function i8lnReplace (text) {
  var matches = text.match(/[^{}]+(?=})/g)

  $.each(matches, function (key, value) {
    text = text.replace('{' + value + '}', i8ln(value))
  })
  return text
}

function isTouchDevice () {
  // Should cover most browsers
  return 'ontouchstart' in window || navigator.maxTouchPoints
}

function getQueryParams () {
  var queryParams = location.search.substring(1)
  return queryParams ? JSON.parse(
  '{"' + queryParams.replace(/&/g, '","')
  .replace(/=/g, '":"') + '"}',
  function (key, value) {
    return (key === '') ? value : decodeURIComponent(value)
  }) : {}
}

//
// Page Ready Exection
//

$(function () {
  if (Push.isSupported) {
    Push.Permission.request()

    var queryParams = getQueryParams()
    if ('centermap' in queryParams) {
      var location = queryParams.centermap.split(',')
      centerMap(location[0], location[1], 20)
    }

    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('message', function (event) {
        if (('task' in event.data) && (event.data.task === 'centermap')) {
          centerMap(event.data.lat, event.data.lng, 20)
        }
      })
    }
  } else {
    console.log('notifications are not supported.')
  }
})

$(function () {
  // populate Navbar Style menu
  $selectStyle = $('#map-style')

  // Load Stylenames, translate entries, and populate lists
  $.getJSON('static/dist/data/mapstyle.min.json').done(function (data) {
    var styleList = []

    $.each(data, function (key, value) {
      styleList.push({
        id: key,
        text: i8ln(value)
      })
    })

    // setup the stylelist
    $selectStyle.select2({
      placeholder: 'Select Style',
      data: styleList,
      minimumResultsForSearch: Infinity
    })

    // setup the list change behavior
    $selectStyle.on('change', function (e) {
      selectedStyle = $selectStyle.val()
      map.setMapTypeId(selectedStyle)
      Store.set('map_style', selectedStyle)
    })

    // recall saved mapstyle
    $selectStyle.val(Store.get('map_style')).trigger('change')
  })

  $selectIconResolution = $('#pokemon-icons')

  $selectIconResolution.select2({
    placeholder: 'Select Icon Resolution',
    minimumResultsForSearch: Infinity
  })

  $selectIconResolution.on('change', function () {
    Store.set('pokemonIcons', this.value)
    redrawPokemon(mapData.pokemons)
    redrawPokemon(mapData.lurePokemons)
  })

  $selectIconSize = $('#pokemon-icon-size')

  $selectIconSize.select2({
    placeholder: 'Select Icon Size',
    minimumResultsForSearch: Infinity
  })

  $selectIconSize.on('change', function () {
    Store.set('iconSizeModifier', this.value)
    redrawPokemon(mapData.pokemons)
    redrawPokemon(mapData.lurePokemons)
  })

  $selectLuredPokestopsOnly = $('#lured-pokestops-only-switch')

  $selectLuredPokestopsOnly.select2({
    placeholder: 'Only Show Lured Pokestops',
    minimumResultsForSearch: Infinity
  })

  $selectLuredPokestopsOnly.on('change', function () {
    Store.set('showLuredPokestopsOnly', this.value)
    updateMap()
  })

  $selectSearchIconMarker = $('#iconmarker-style')

  $.getJSON('static/dist/data/searchmarkerstyle.min.json').done(function (data) {
    searchMarkerStyles = data
    var searchMarkerStyleList = []

    $.each(data, function (key, value) {
      searchMarkerStyleList.push({
        id: key,
        text: value.name
      })
    })

    $selectSearchIconMarker.select2({
      placeholder: 'Select Icon Marker',
      data: searchMarkerStyleList,
      minimumResultsForSearch: Infinity
    })

    $selectSearchIconMarker.on('change', function (e) {
      var selectSearchIconMarker = $selectSearchIconMarker.val()
      Store.set('searchMarkerStyle', selectSearchIconMarker)
      updateSearchMarker(selectSearchIconMarker)
    })

    $selectSearchIconMarker.val(Store.get('searchMarkerStyle')).trigger('change')

    updateSearchMarker(Store.get('lockMarker'))
  })

  // Load notification distances and populate lists
  $.getJSON('static/dist/data/notificationdistance.min.json').done(function (data) {
    var notificationDistanceList = []

    $.each(data, function (key, value) {
      notificationDistanceList.push({
        id: key,
        text: i8lnReplace(value['text'])
      })

      notificationDistances[key] = {type: value['type'], value: value['value']}
    })

    $selectNotificationNotify = $('#notify-notification')

    $selectNotificationNotify.select2({
      placeholder: i8ln('Select Distance'),
      data: notificationDistanceList,
      minimumResultsForSearch: Infinity
    })

    $selectNotificationNotify.on('change', function (e) {
      Store.set('select_notification_notify', this.value)
    })

    $selectNotificationNotify.val(Store.get('select_notification_notify')).trigger('change')

    $selectSoundNotify = $('#notify-sound')

    $selectSoundNotify.select2({
      placeholder: i8ln('Select Distance'),
      data: notificationDistanceList,
      minimumResultsForSearch: Infinity
    })

    $selectSoundNotify.on('change', function (e) {
      Store.set('select_sound_notify', this.value)
    })

    $selectSoundNotify.val(Store.get('select_sound_notify')).trigger('change')

    $selectTexttospeechNotify = $('#notify-texttospeech')

    $selectTexttospeechNotify.select2({
      placeholder: i8ln('Select Distance'),
      data: notificationDistanceList,
      minimumResultsForSearch: Infinity
    })

    $selectTexttospeechNotify.on('change', function (e) {
      Store.set('select_texttospeech_notify', this.value)
    })

    $selectTexttospeechNotify.val(Store.get('select_texttospeech_notify')).trigger('change')
  })

  // Load sound packs and populate list
  $.getJSON('static/sounds/audiosprites.min.json').done(function (data) {
    var audiospriteList = []
    $.each(data, function (key, value) {
      audiospriteList.push({
        id: value['id'],
        text: i8lnReplace(value['text'])
      })
      audiosprites[value['id']] = {id: value['id'], type: value['type'], src: value['src']}
    })

    $selectAudiospriteNotify = $('#notify-audiosprite')

    $selectAudiospriteNotify.select2({
      placeholder: i8ln('Select Sound Pack'),
      data: audiospriteList,
      minimumResultsForSearch: Infinity
    })

    $selectAudiospriteNotify.on('change', function (e) {
      soundNotify.load('static/sounds/' + audiosprites[this.value].id + '/' + audiosprites[this.value].src, 'static/sounds/' + audiosprites[this.value].id + '/')
      Store.set('select_audiosprite_notify', this.value)
    })

    $selectAudiospriteNotify.val(Store.get('select_audiosprite_notify')).trigger('change')
  })

  $selectNearbyNotify = $('#notify-nearby')

  $selectNearbyNotify.select2({
    placeholder: i8ln('Select Notifications'),
    data: [{id: 1, text: i8ln('Push')}, {id: 2, text: i8ln('Sound')}, {id: 3, text: i8ln('Voice')}]
  })

  $selectNearbyNotify.on('change', function (e) {
    Store.set('select_nearby_notify', $selectNearbyNotify.val().map(Number))
  })

  $selectNearbyNotify.val(Store.get('select_nearby_notify')).trigger('change')

  $selectNearbyDistanceNotify = $('#notify-nearbydistance')

  $selectNearbyDistanceNotify.select2({
    placeholder: i8ln('Select Distance'),
    minimumResultsForSearch: Infinity,
    data: [{id: 1, text: i8ln('Nearby')},
      {id: 100, text: i8lnReplace('{Less than} 100 {Meters}')},
      {id: 150, text: i8lnReplace('{Less than} 150 {Meters}')},
      {id: 200, text: i8lnReplace('{Less than} 200 {Meters}')},
      {id: 250, text: i8lnReplace('{Less than} 250 {Meters}')},
      {id: 300, text: i8lnReplace('{Less than} 300 {Meters}')},
      {id: 350, text: i8lnReplace('{Less than} 350 {Meters}')},
      {id: 400, text: i8lnReplace('{Less than} 400 {Meters}')},
      {id: 450, text: i8lnReplace('{Less than} 450 {Meters}')},
      {id: 500, text: i8lnReplace('{Less than} 500 {Meters}')}]
  })

  $selectNearbyDistanceNotify.on('change', function (e) {
    Store.set('select_nearbydistance_notify', this.value)
  })

  $selectNearbyDistanceNotify.val(Store.get('select_nearbydistance_notify')).trigger('change')
})

$(function () {
  function formatState (state) {
    if (!state.id) {
      return state.text
    }
    var $state = $(
      '<span><i class="pokemon-sprite n' + state.element.value.toString() + '"></i> ' + state.text + '</span>'
    )
    return $state
  }

  if (Store.get('startAtUserLocation')) {
    centerMapOnLocation()
  }

  $selectExclude = $('#exclude-pokemon')
  $selectPokemonNotify = $('#notify-pokemon')
  $selectRarityNotify = $('#notify-rarity')
  var numberOfPokemon = 151

  // Load pokemon names and populate lists
  $.getJSON('static/dist/data/pokemon.min.json').done(function (data) {
    var pokeList = []

    $.each(data, function (key, value) {
      if (key > numberOfPokemon) {
        return false
      }
      var _types = []
      pokeList.push({
        id: key,
        text: i8ln(value['name']) + ' - #' + key
      })
      value['name'] = i8ln(value['name'])
      value['rarity'] = i8ln(value['rarity'])
      $.each(value['types'], function (key, pokemonType) {
        _types.push({
          'type': i8ln(pokemonType['type']),
          'color': pokemonType['color']
        })
      })
      value['types'] = _types
      idToPokemon[key] = value
    })

    // setup the filter lists
    $selectExclude.select2({
      placeholder: i8ln('Select Pokémon'),
      data: pokeList,
      templateResult: formatState
    })
    $selectPokemonNotify.select2({
      placeholder: i8ln('Select Pokémon'),
      data: pokeList,
      templateResult: formatState
    })
    $selectRarityNotify.select2({
      placeholder: i8ln('Select Rarity'),
      data: [i8ln('Common'), i8ln('Uncommon'), i8ln('Rare'), i8ln('Very Rare'), i8ln('Ultra Rare')],
      templateResult: formatState
    })

    // setup list change behavior now that we have the list to work from
    $selectExclude.on('change', function (e) {
      excludedPokemon = $selectExclude.val().map(Number)
      clearStaleMarkers()
      Store.set('remember_select_exclude', excludedPokemon)
    })
    $selectPokemonNotify.on('change', function (e) {
      notifiedPokemon = $selectPokemonNotify.val().map(Number)
      Store.set('remember_select_notify', notifiedPokemon)
    })
    $selectRarityNotify.on('change', function (e) {
      notifiedRarity = $selectRarityNotify.val().map(String)
      Store.set('remember_select_rarity_notify', notifiedRarity)
    })

    // recall saved lists
    $selectExclude.val(Store.get('remember_select_exclude')).trigger('change')
    $selectPokemonNotify.val(Store.get('remember_select_notify')).trigger('change')
    $selectRarityNotify.val(Store.get('remember_select_rarity_notify')).trigger('change')
  })

  // run interval timers to regularly update map and timediffs
  window.setInterval(updateLabelDiffTime, 1000)
  window.setInterval(updateMap, 5000)
  window.setInterval(function () {
    if (navigator.geolocation && Store.get('geoLocate')) {
      navigator.geolocation.getCurrentPosition(function (position) {
        var baseURL = location.protocol + '//' + location.hostname + (location.port ? ':' + location.port : '')
        var lat = position.coords.latitude
        var lon = position.coords.longitude

        // the search function makes any small movements cause a loop. Need to increase resolution
        if (getPointDistance(searchMarker.getPosition(), (new google.maps.LatLng(lat, lon))) > 40) {
          $.post(baseURL + '/next_loc?lat=' + lat + '&lon=' + lon).done(function () {
            var center = new google.maps.LatLng(lat, lon)
            map.panTo(center)
            searchMarker.setPosition(center)
          })
        }
      })
    }
  }, 1000)

  // Wipe off/restore map icons when switches are toggled
  function buildSwitchChangeListener (data, dataType, storageKey) {
    return function () {
      Store.set(storageKey, this.checked)
      if (this.checked) {
        updateMap()
      } else {
        $.each(dataType, function (d, dType) {
          $.each(data[dType], function (key, value) {
            // for any marker you're turning off, you'll want to wipe off the range
            if (data[dType][key].marker.rangeCircle) {
              data[dType][key].marker.rangeCircle.setMap(null)
              delete data[dType][key].marker.rangeCircle
            }
            if (storageKey !== 'showRanges') data[dType][key].marker.setMap(null)
          })
          if (storageKey !== 'showRanges') data[dType] = {}
        })
        if (storageKey === 'showRanges') {
          updateMap()
        }
      }
    }
  }

  // Setup UI element interactions
  $('#gyms-switch').change(buildSwitchChangeListener(mapData, ['gyms'], 'showGyms'))
  $('#pokemon-switch').change(buildSwitchChangeListener(mapData, ['pokemons'], 'showPokemon'))
  $('#scanned-switch').change(buildSwitchChangeListener(mapData, ['scanned'], 'showScanned'))
  $('#spawnpoints-switch').change(buildSwitchChangeListener(mapData, ['spawnpoints'], 'showSpawnpoints'))
  $('#ranges-switch').change(buildSwitchChangeListener(mapData, ['gyms', 'pokemons', 'pokestops'], 'showRanges'))

  $('#pokestops-switch').change(function () {
    var options = {
      'duration': 500
    }
    var wrapper = $('#lured-pokestops-only-wrapper')
    if (this.checked) {
      wrapper.show(options)
    } else {
      wrapper.hide(options)
    }
    return buildSwitchChangeListener(mapData, ['pokestops'], 'showPokestops').bind(this)()
  })

  $('#notify-switch').change(function () {
    Store.set('notify', this.checked)
  })

  $('#geoloc-switch').change(function () {
    $('#next-location').prop('disabled', this.checked)
    $('#next-location').css('background-color', this.checked ? '#e0e0e0' : '#ffffff')
    if (!navigator.geolocation) {
      this.checked = false
    } else {
      Store.set('geoLocate', this.checked)
    }
  })

  $('#lock-marker-switch').change(function () {
    Store.set('lockMarker', this.checked)
    searchMarker.setDraggable(!this.checked)
  })

  $('#search-switch').change(function () {
    searchControl(this.checked ? 'on' : 'off')
  })

  $('#start-at-user-location-switch').change(function () {
    Store.set('startAtUserLocation', this.checked)
  })

  if ($('#nav-accordion').length) {
    $('#nav-accordion').accordion({
      active: 0,
      collapsible: true,
      heightStyle: 'content'
    })
  }
})

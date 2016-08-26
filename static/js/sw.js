var notificationBlacklist = [];
var lastKnownLocation = [];

function firstWindowClient() {
  return clients.matchAll({ type: 'window' }).then(function(windowClients) {
    return windowClients.length ? windowClients[0] : Promise.reject("No clients");
  });
}

self.addEventListener('install' , function(event) { event.waitUntil(skipWaiting()  ); });
self.addEventListener('activate', function(event) { event.waitUntil(clients.claim()); });
self.addEventListener('notificationclick', function(event) {

  var item = event.notification.data;

  var dateObj = new Date(item.disappear_time);
  
  var despawn_time = dateObj.getHours() + ":" + dateObj.getMinutes() + ":" + dateObj.getSeconds() ;
  
  if( event.action === 'navigate' ){
  
    navigationURI = (item.isMobile ? "google.navigation:q=" : "http://google.com/maps/dir/Current+Location/") + item.latitude + "," + item.longitude;
    clients.openWindow("./?launch_intent=" + encodeURIComponent(navigationURI) );
	//todo: close notification pulldown if possible - do this by shifting focus to the new open window, if js will let us	
    
  } else if( event.action === 'share' ){
  
    
  } else if( event.action === 'removeMarker' ){
  
    var promise = Promise.resolve();
    promise = promise.then(firstWindowClient).then(function(client) {
      client.postMessage({
        action: 'removeMarker',
        encounter_id: item.encounter_id
      });
    });
    event.waitUntil(promise);
    notificationBlacklist.push(item.encounter_id);
    close_by_encounter(item.encounter_id);
	
  
  } else if( event.action === 'excludePokemon' ){
  
    var promise = Promise.resolve();
    promise = promise.then(firstWindowClient).then(function(client) {
      client.postMessage({
        action: 'excludePokemon',
        pokemon_id: item.pokemon_id
      });
    });
    event.waitUntil(promise);
    notificationBlacklist.push(item.encounter_id);
    close_by_encounter(item.encounter_id);
	
  
  } else {
  
    var centerAndFocus = function(client) {
      client.postMessage({
        action: 'clicked',
        lat: item.latitude,
        lng: item.longitude
      });
      return client.focus();
    }
    //promise. first try to focus existing window, if that fails open a new window
    var promise = Promise.resolve();
    promise = promise.then(firstWindowClient).then(centerAndFocus);
    promise = promise.catch(function() { clients.openWindow(item.url); });
    event.waitUntil(promise);
  }
});

self.addEventListener('notificationclose', function(event) {
  var item = event.notification.data;
  close_by_encounter(item.encounter_id);
  notificationBlacklist.push(item.encounter_id);
});

function get_distance(lat1,lon1,lat2,lon2) {
  function toRad(x) { return x * Math.PI / 180; }
  var R = 6371; // km
  var x1 = lat2 - lat1;
  var dLat = toRad(x1);
  var x2 = lon2 - lon1;
  var dLon = toRad(x2)
  var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  var d = R * c;
  return Math.round(d * 100) * 10 ;
}

function createOrUpdateNotification(data){

    item = data.item;
    
    var blacklistIndex = notificationBlacklist.indexOf(item.encounter_id);
        
    if( blacklistIndex > -1 ) {
        notificationBlacklist.splice( blacklistIndex, 1 );
        return false;
    }
    
    if ( item.disappear_time - Date.now() > 0) {
      if( lastKnownLocation.length > 0  ) {
        markerLat = lastKnownLocation[0];
        markerLng = lastKnownLocation[1];
      } else{
        markerLat = data.locationMarker.lat;
        markerLng = data.locationMarker.lng;
      }
      var title = item.pokemon_name + ' is ' + get_distance(item.latitude,item.longitude,markerLat,markerLng) + ' meters away';
      var min_remain = Math.round((item.disappear_time - Date.now())/60000);
      if( min_remain == 1 ) var maybe_s = '';
      else var maybe_s = 's';
      var body = 'for ' + min_remain + ' more minute' + maybe_s;
    } else if ( item.disappear_time - Date.now() > -120000 ) {
      var title = item.pokemon_name + ' despawned.';
      var body = '';
    } else {
      close_by_encounter(item.encounter_id);
      return false;
    }
      //close_by_encounter(item.encounter_id);
    
    var toReturn = self.registration.showNotification(title, {
      icon: 'static/icons/' + item['pokemon_id'] + '.png',
      body: body,
      tag: item['encounter_id'],
      renotify: false,
      requireInteraction: true,
      timestamp: item['disappear_time'],
      sound: 'sounds/ding.mp3',
	  vibrate: [200, 100, 200, 100, 200, 100, 200],
      actions: [
        {action:'navigate'      , title:'Navigate', icon:'https://lh3.googleusercontent.com/PZakD9b5_pGwjig2tEdbDTbXTO6gPQRUgAXSOYL7EsYVMwtn5-1y8Egh9MUB68K_AkM'},
        {action:'excludePokemon', title:'Exclude' , icon:'https://lh3.googleusercontent.com/FAM7OlgYDU-GUIigp9SEWonHCLa6hJ9WgzrnK0QIxiRP6L8vXZSlrzC7IJddsrChJid3Tls9'},
        {action:'removeMarker'  , title:'Remove'  , icon:'https://lh3.googleusercontent.com/DPv8X8D-7Q8macK80sQ5QKYDtqlRAgg21ytegNisDA9CTKrbqvCvIGU2tzXqMoaCGQ'}
      ],
      data: {
        latitude: item['latitude'],
        longitude: item['longitude'],
        url: data.url,
        encounter_id: item['encounter_id'],
		pokemon_name: item['pokemon_name'],
		pokemon_id: item['pokemon_id'],
		disappear_time: item['disappear_time'],
	    isMobile: data.isMobile,
      }
    });
    
    setTimeout( createOrUpdateNotification.bind(null,data), 20000 );
    
    return toReturn;
}

var receiveMessage = function(event){
  
  if (event.data.action === 'showNotification' ){
    lastKnownLocation = [event.data.locationMarker.lat,event.data.locationMarker.lng];
    event.waitUntil(createOrUpdateNotification(event.data));  
    firstWindowClient().then(function(client) { client.postMessage({ action: 'playaudio' }); });
    
  } else if (event.data.action === 'updateLocation') {
    lastKnownLocation = [event.data.locationMarker.lat,event.data.locationMarker.lng];
  } else {
  
    console.log('message received:', event)
  
  }
  
}

self.addEventListener('message',receiveMessage);
self.addEventListener('push',receiveMessage);

function close_by_encounter(eid){
  self.registration.getNotifications().then(function(notifications){ notifications.forEach(function(notification){
    if( notification.data.encounter_id === eid ) notification.close()
  });});
}

function close_all(){
    self.registration.getNotifications().then(function(notifications){ notifications.forEach(function(notification){notification.close()}); });
}

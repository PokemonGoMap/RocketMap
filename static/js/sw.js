/* eslint-env serviceworker */

self.addEventListener('install', function (event) {
  return self.skipWaiting()
})

self.addEventListener('activate', function (event) {
  return self.clients.claim()
})

self.addEventListener('notificationclick', function (event) {
    // close the notification
  event.notification.close()
  var data = event.notification.data

  // open the app after click notification
  event.waitUntil(
    clients.matchAll({
      includeUncontrolled: true,
      type: 'window'
    }).then(function (clientList) {
      for (var i = 0; i < clientList.length; i++) {
        var client = clientList[i]
        if ('focus' in client) {
          if (('lat' in data) && ('lng' in data)) {
            client.postMessage({
              task: 'centermap',
              lat: data.lat,
              lng: data.lng
            })
          }
          return client.focus()
        }
      }
          // app not found, open a new one
      if (clientList.length === 0) {
        if (clients.openWindow) {
          if ('url' in data) {
            return clients.openWindow(data.url)
          } else {
            return clients.openWindow('/')
          }
        }
      }
    })
  )
})

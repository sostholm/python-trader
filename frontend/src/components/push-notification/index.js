// import * as serviceWorker from 'serviceWorker';



export function notification() {

}

export function displayNotification() {
  if (Notification.permission == 'granted') {
    navigator.serviceWorker.getRegistration().then(function (reg) {
      var options = {
        body: 'Here is a notification body!',
        icon: 'images/example.png',
        vibrate: [100, 50, 100],
        data: {
          dateOfArrival: Date.now(),
          primaryKey: 1
        }
      };
      reg.showNotification('Hello world!', options);

      reg.pushManager.getSubscription().then(function (sub) {
        if (sub === null) {
          // Update UI to ask user to register for Push
          console.log('Not subscribed to push service!');
          subscribeUser()
        } else {
          // We have a subscription, update the database
          console.log('Subscription object: ', JSON.stringify(sub));
        }
      });

    });
  }
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/')
    ;
  let rawData

  rawData = atob(base64);
  return Uint8Array.from([...rawData].map((char) => char.charCodeAt(0)));
}

const applicationServerKey = urlBase64ToUint8Array('BOnPOdBMs6jPhfJ_F9EpeyiPOc2dX4niC6-V_zSZcRSn2TwRkI4i_TeLqxiSTSiPgm89355SeAZFZnJp9QMfWqY')

export async function subscribeUser(func) {
  Notification.requestPermission(status => {
    console.log('Notification permission status:', status);
  });
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then(function (reg) {

      reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: applicationServerKey
      }).then(async function (sub) {
        console.log('Endpoint URL: ', sub.endpoint);
        console.log('Origin: ', new URL(sub.endpoint).origin)
        console.log(sub.toJSON())
        func(sub.toJSON())
        try {
          await reg.periodicSync.register('sub-refresh', {
            minInterval: 23 * 60 * 60 * 1000,
          })
        } catch {
          console.log('Periodic Sync could not be registered!');
        }
        return sub
      }).catch(function (e) {
        if (Notification.permission === 'denied') {
          console.warn('Permission for notifications was denied');
        } else {
          console.error('Unable to subscribe to push', e);
        }
      });
    })

  }
}
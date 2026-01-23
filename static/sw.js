// Service Worker for Fencing Drill PWA
const CACHE_NAME = 'fencing-drill-v2';
const AUDIO_CACHE_NAME = 'fencing-drill-audio-v1';

// Static assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/static/js/audio.js',
  '/static/manifest.json'
];

// Audio files to cache
const AUDIO_ASSETS = [
  '/static/audio/en_garde.mp3',
  '/static/audio/marche.mp3',
  '/static/audio/rompe.mp3',
  '/static/audio/fendez.mp3',
  '/static/audio/allongez.mp3',
  '/static/audio/remise.mp3',
  '/static/audio/balancez.mp3',
  '/static/audio/double_marche.mp3',
  '/static/audio/bond_avant.mp3',
  '/static/audio/bond_arriere.mp3',
  '/static/audio/repos.mp3',
  '/static/audio/termine.mp3',
  '/static/audio/allez.mp3',
  '/static/audio/halte.mp3',
  '/static/audio/pret.mp3',
  '/static/audio/un.mp3',
  '/static/audio/deux.mp3',
  '/static/audio/trois.mp3'
];

// Install event - cache static and audio assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(CACHE_NAME).then((cache) => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      }),
      // Cache audio assets separately (larger files)
      caches.open(AUDIO_CACHE_NAME).then((cache) => {
        console.log('[SW] Caching audio assets');
        return cache.addAll(AUDIO_ASSETS);
      })
    ]).then(() => {
      console.log('[SW] All assets cached');
      return self.skipWaiting();
    })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME && name !== AUDIO_CACHE_NAME)
          .map((name) => {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    }).then(() => {
      console.log('[SW] Activated');
      return self.clients.claim();
    })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Skip SSE endpoints (must be network-only)
  if (url.pathname.includes('/session/stream')) {
    return;
  }

  // Audio files - cache first strategy
  if (url.pathname.startsWith('/static/audio/')) {
    event.respondWith(
      caches.open(AUDIO_CACHE_NAME).then((cache) => {
        return cache.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          return fetch(event.request).then((networkResponse) => {
            cache.put(event.request, networkResponse.clone());
            return networkResponse;
          });
        });
      })
    );
    return;
  }

  // Static assets - cache first, network fallback
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(event.request).then((networkResponse) => {
          return caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, networkResponse.clone());
            return networkResponse;
          });
        });
      })
    );
    return;
  }

  // HTML pages - network first, cache fallback
  if (event.request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(
      fetch(event.request)
        .then((networkResponse) => {
          return caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, networkResponse.clone());
            return networkResponse;
          });
        })
        .catch(() => {
          return caches.match(event.request).then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse;
            }
            // Return cached root as fallback
            return caches.match('/');
          });
        })
    );
    return;
  }

  // Default - network first, cache fallback
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        return caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, networkResponse.clone());
          return networkResponse;
        });
      })
      .catch(() => {
        return caches.match(event.request);
      })
  );
});

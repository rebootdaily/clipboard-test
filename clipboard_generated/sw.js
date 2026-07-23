// Clipboard service worker -- automatic cache versioning.
//
// The cache name embeds the app's version (8.0.0, stamped by
// generate.py from the repo-root VERSION file -- see ARCHITECTURE.md).
// Every release therefore gets a brand-new cache name automatically; the
// activate handler deletes every cache from a previous version, so old
// JS/CSS/HTML can never linger. The fetch handler always tries the network
// first with {cache:'no-store'} (bypassing GitHub Pages' HTTP caching and
// Safari's aggressive disk cache for installed home-screen apps) and only
// falls back to the cache when the network is unavailable, so a plain
// refresh always gets the latest release without the user ever needing to
// clear Safari website data. The cache exists purely for offline use in
// the field.

const CACHE_NAME = 'clipboard-cache-8.0.0';
const CACHE_PREFIX = 'clipboard-cache-';

self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches
      .keys()
      .then(names =>
        Promise.all(
          names
            .filter(name => name.startsWith(CACHE_PREFIX) && name !== CACHE_NAME)
            .map(name => caches.delete(name))
        )
      )
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  event.respondWith(
    fetch(request, { cache: 'no-store' })
      .then(response => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
        return response;
      })
      .catch(() => caches.match(request))
  );
});

// Bump this on every deploy that changes JS/CSS so old caches get discarded.
const CACHE_NAME = "angie-cache-v2";

const CORE_ASSETS = [
  "/static/css/style.css",
  "/static/js/app.js",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png",
  "/offline",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(CORE_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const { request } = event;

  // Never cache API calls or the streaming chat endpoint.
  if (request.url.includes("/api/")) return;

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request).catch(() => caches.match("/offline"))
    );
    return;
  }

  const isCode = request.url.endsWith(".js") || request.url.endsWith(".css");

  if (isCode) {
    // NETWORK-FIRST for JS/CSS: always try to get the latest file first,
    // and only fall back to the cached copy if the network is unreachable.
    // This is what makes code fixes actually show up on the next reload
    // instead of a stale cached script running forever.
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // CACHE-FIRST for everything else (images, icons) - these rarely change
  // and don't need to be re-verified on every load.
  event.respondWith(
    caches.match(request).then((cached) => {
      return (
        cached ||
        fetch(request)
          .then((response) => {
            if (response.ok && request.method === "GET") {
              const clone = response.clone();
              caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
            }
            return response;
          })
          .catch(() => cached)
      );
    })
  );
});

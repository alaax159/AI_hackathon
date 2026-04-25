// Minimal service worker: cache the shell + Leaflet, serve last-known
// /ask responses when offline. Connectivity is unreliable in much of the
// West Bank and Gaza — the app must keep working without it.

const CACHE = "paljustice-v2";
const SHELL = [
  "/",
  "/manifest.json",
  "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
  "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL).catch(() => {}))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  const url = new URL(req.url);

  // POST /ask: network-first, then cached fallback keyed by the request body.
  if (req.method === "POST" && url.pathname === "/ask") {
    e.respondWith(handleAsk(req));
    return;
  }
  if (req.method !== "GET") return;

  // Static + same-origin: cache-first, fall back to network, cache the response.
  e.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req)
        .then((resp) => {
          if (resp && resp.status === 200 && resp.type === "basic") {
            const copy = resp.clone();
            caches.open(CACHE).then((c) => c.put(req, copy));
          }
          return resp;
        })
        .catch(() => caches.match("/"));
    })
  );
});

async function handleAsk(req) {
  const body = await req.clone().text();
  const cacheKey = new Request("/__ask_cache__/" + hash(body), { method: "GET" });
  try {
    const fresh = await fetch(req.clone());
    if (fresh && fresh.ok) {
      const copy = fresh.clone();
      caches.open(CACHE).then((c) => c.put(cacheKey, copy));
    }
    return fresh;
  } catch (e) {
    const cached = await caches.match(cacheKey);
    if (cached) return cached;
    return new Response(JSON.stringify({
      answer: "You are offline. Please connect to the internet to receive a fresh answer.",
      intent: { label: "general", confidence: 0, matched: [] },
      sources: [],
      clinics: [],
      triage: { level: "standard", color: "green", label: "Offline", deadline_hint: "" },
      action_plan: [],
      language: "en",
    }), { status: 200, headers: { "Content-Type": "application/json" } });
  }
}

function hash(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = ((h << 5) - h + s.charCodeAt(i)) | 0;
  return Math.abs(h).toString(36);
}

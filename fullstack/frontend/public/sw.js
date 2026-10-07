// Cache-first app shell, network-first for API; register from layout: navigator.serviceWorker.register("/sw.js")
const SHELL = "aura-shell-v1";
self.addEventListener("install", (e) => e.waitUntil(caches.open(SHELL).then((c) => c.addAll(["/", "/manifest.json"]))));
self.addEventListener("activate", (e) => e.waitUntil(caches.keys().then((k) => Promise.all(k.filter((x) => x !== SHELL).map((x) => caches.delete(x))))));
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  const api = new URL(e.request.url).pathname.startsWith("/v1/");
  e.respondWith(api ? fetch(e.request).catch(() => caches.match(e.request))
    : caches.match(e.request).then((hit) => hit || fetch(e.request).then((r) => { const c = r.clone(); caches.open(SHELL).then((s) => s.put(e.request, c)); return r; })));
});

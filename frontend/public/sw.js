// Service worker mínimo: hace la app instalable. El modo offline real llega en una fase posterior.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", () => {});

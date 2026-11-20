// 심플 실측 서비스 워커 — "앱 설치"(PWA)와 오프라인(현장에서 인터넷이 안 될 때) 실행용
// 네트워크 먼저: 인터넷이 되면 항상 최신(GitHub Pages)을 쓰고 받은 것을 저장, 안 되면 저장본으로 실행
// 캐시 이름은 'simplemeasure-'로 시작 — 심플 캐드(sw.js, 'simplecad-')와 서로 지우지 않게
var CACHE = 'simplemeasure-v7';
var CORE = ['./', 'index.html', 'manifest.webmanifest', '../mall-catalog.js',
  '../icons/icon-192.png?v=2', '../icons/icon-512.png?v=2', '../icons/apple-touch-icon.png?v=2'];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(CORE); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k.indexOf('simplemeasure-') === 0 && k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener('fetch', function (e) {
  var req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== self.location.origin) return;
  e.respondWith(fetch(req).then(function (res) {
    if (res.ok) { var cp = res.clone(); caches.open(CACHE).then(function (c) { c.put(req, cp); }); }
    return res;
  }).catch(function () {
    return caches.open(CACHE).then(function (c) {
      return c.match(req, { ignoreSearch: true }).then(function (hit) {
        return hit || (req.mode === 'navigate' ? c.match('index.html') : undefined);
      });
    });
  }));
});

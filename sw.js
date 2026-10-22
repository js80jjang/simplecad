// 심플 캐드 서비스 워커 — "앱 설치"(PWA)와 오프라인 실행용
// 앱 파일은 "네트워크 먼저": 인터넷이 되면 항상 최신(GitHub Pages)을 쓰고 받은 것을 저장해 두며,
// 인터넷이 안 되면 저장해 둔 것으로 실행. 제품 온장 이미지(mall-img/)는 저장된 것 먼저(잘 안 바뀜).
// 다른 사이트(Firebase 등) 요청은 건드리지 않음.
var CACHE = 'simplecad-v2'; // 올리면 예전 저장본(이미지 포함)을 지우고 새로 받음 — mall-img 화질 바꿀 때 등
var CORE = ['./', 'index.html', 'dxf-form.js', 'mall-catalog.js', 'manifest.webmanifest',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png'];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(CORE); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener('fetch', function (e) {
  var req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== self.location.origin) return;
  if (url.pathname.indexOf('/mall-img/') >= 0) { // 저장된 것 먼저
    e.respondWith(caches.match(req).then(function (hit) {
      return hit || fetch(req).then(function (res) {
        if (res.ok) { var cp = res.clone(); caches.open(CACHE).then(function (c) { c.put(req, cp); }); }
        return res;
      });
    }));
    return;
  }
  e.respondWith(fetch(req).then(function (res) { // 네트워크 먼저
    if (res.ok) { var cp = res.clone(); caches.open(CACHE).then(function (c) { c.put(req, cp); }); }
    return res;
  }).catch(function () {
    return caches.match(req, { ignoreSearch: true }).then(function (hit) {
      return hit || (req.mode === 'navigate' ? caches.match('index.html') : undefined);
    });
  }));
});

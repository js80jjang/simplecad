# 세라믹 심플 캐드 런처: 기본 브라우저로 index.html 열기
# (제품 목록은 윤현몰 목록 mall-catalog.js만 씀 — 매일 GitHub Actions가 갱신)
$HtmlSrc = Join-Path $PSScriptRoot 'index.html'
Start-Process $HtmlSrc
Write-Host "브라우저로 열기: $HtmlSrc"
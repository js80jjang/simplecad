# 개발용 로컬 서버 (브라우저 저장소/파일 fetch가 되는 환경에서 index.html 테스트)
#   powershell -ExecutionPolicy Bypass -File tools\serve.ps1            → http://localhost:8765/
#   powershell -ExecutionPolicy Bypass -File tools\serve.ps1 -Dxf C:\경로\도면.dxf  → /real.dxf 로 DXF 제공
param([string]$Dxf = '', [int]$Port = 8765)
$Root = Split-Path -Parent $PSScriptRoot
$l = New-Object Net.HttpListener
$l.Prefixes.Add("http://localhost:$Port/")
$l.Start()
Write-Host "http://localhost:$Port/ (Ctrl+C 로 종료)"
while ($l.IsListening) {
  $ctx = $l.GetContext()
  $path = $ctx.Request.Url.AbsolutePath
  try {
    if ($path -eq '/real.dxf' -and $Dxf) { $file = $Dxf; $type = 'application/octet-stream' }
    elseif ($path -eq '/' -or $path -eq '/index.html') { $file = Join-Path $Root 'index.html'; $type = 'text/html; charset=utf-8' }
    else { $file = Join-Path $Root ([Uri]::UnescapeDataString($path.TrimStart('/'))); $type = 'application/javascript; charset=utf-8' }
    if (Test-Path -LiteralPath $file) {
      $bytes = [IO.File]::ReadAllBytes($file)
      $ctx.Response.ContentType = $type
      $ctx.Response.ContentLength64 = $bytes.Length
      $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length)
    } else { $ctx.Response.StatusCode = 404 }
  } catch { $ctx.Response.StatusCode = 500 }
  $ctx.Response.Close()
}

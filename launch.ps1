# 세라믹 가공비 계산 런처
# - 세라믹제품목록.xlsx에서 제품 데이터를 읽어 제품목록.js 생성
# - 기본 브라우저로 index.html 열기
# 엑셀/파이썬 없이 동작하도록 xlsx(zip) 내부 XML을 직접 읽는다.

$ErrorActionPreference = 'Stop'
$BaseDir = $PSScriptRoot
$Xlsx    = Join-Path $BaseDir '세라믹제품목록.xlsx'
$JsPath  = Join-Path $BaseDir '제품목록.js'
$HtmlSrc = Join-Path $BaseDir 'index.html'

function Read-ZipXml($zip, $name) {
    $entry = $zip.GetEntry($name)
    if (-not $entry) { return $null }
    $reader = New-Object IO.StreamReader($entry.Open(), [Text.Encoding]::UTF8)
    try { [xml]$reader.ReadToEnd() } finally { $reader.Dispose() }
}

# 첫 번째 시트를 행(셀 값 배열) 목록으로 반환
function Read-XlsxRows($path) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [IO.Compression.ZipFile]::OpenRead($path)
    try {
        $shared = @()
        $sst = Read-ZipXml $zip 'xl/sharedStrings.xml'
        if ($sst) {
            # 서식 있는 문자열(<r><t>)도 합쳐서 읽기
            $shared = @($sst.sst.si | ForEach-Object { ($_.GetElementsByTagName('t') | ForEach-Object { $_.InnerText }) -join '' })
        }
        $sheet = Read-ZipXml $zip 'xl/worksheets/sheet1.xml'
        $rows = @()
        foreach ($row in $sheet.worksheet.sheetData.row) {
            $cells = @{}
            $max = -1
            foreach ($c in $row.c) {
                $col = 0
                foreach ($ch in ($c.r -replace '\d', '').ToCharArray()) { $col = $col * 26 + ([int]$ch - 64) }
                $col--
                $v = $null
                if ($c.t -eq 's') { $v = $shared[[int]$c.v] }
                elseif ($c.t -eq 'inlineStr') { $v = $c.is.InnerText }
                elseif ($c.v) { $v = [string]$c.v }
                $cells[$col] = $v
                if ($col -gt $max) { $max = $col }
            }
            $arr = New-Object object[] ($max + 1)
            foreach ($k in $cells.Keys) { $arr[$k] = $cells[$k] }
            $rows += , $arr
        }
        return , $rows
    } finally { $zip.Dispose() }
}

function Read-Catalog {
    if (-not (Test-Path -LiteralPath $Xlsx)) { return @() }
    try { $rows = Read-XlsxRows $Xlsx }
    catch { Write-Host "엑셀 읽기 실패: $_"; return @() }
    if ($rows.Count -eq 0) { return @() }

    # 헤더 행 탐지
    $hdrIdx = 0
    for ($ri = 0; $ri -lt [Math]::Min(5, $rows.Count); $ri++) {
        $joined = ($rows[$ri] | ForEach-Object { [string]$_ }) -join ' '
        if ($joined -match '제품명|품명|사이즈|규격') { $hdrIdx = $ri; break }
    }

    $hdr = $rows[$hdrIdx]
    $nc = 1; $sc = 2
    for ($ci = 0; $ci -lt $hdr.Count; $ci++) {
        $v = [string]$hdr[$ci]
        if ($v -match '제품명|품명|Name|name') { $nc = $ci }
        if ($v -match '사이즈|규격|Size|size') { $sc = $ci }
    }

    $catalog = @()
    for ($ri = $hdrIdx + 1; $ri -lt $rows.Count; $ri++) {
        $row = $rows[$ri]
        $name = if ($nc -lt $row.Count) { ([string]$row[$nc]).Trim() } else { '' }
        $size = if ($sc -lt $row.Count) { ([string]$row[$sc]).Trim() } else { '' }
        if (-not $name -or $name -eq 'nan' -or ($name -replace '\.', '') -match '^\d+$') { continue }
        $catalog += [pscustomobject]@{ name = $name; size = $size }
    }
    Write-Host "제품 $($catalog.Count)개 로드됨"
    return $catalog
}

function ConvertTo-JsString($s) {
    '"' + ($s -replace '\\', '\\' -replace '"', '\"' -replace "`r", '\r' -replace "`n", '\n' -replace "`t", '\t') + '"'
}

$catalog = @(Read-Catalog)
$items = $catalog | ForEach-Object { '{"name": ' + (ConvertTo-JsString $_.name) + ', "size": ' + (ConvertTo-JsString $_.size) + '}' }
$json = '[' + ($items -join ', ') + ']'

# HTML 파일은 수정하지 않음 - 제품목록.js 에만 카탈로그 기록
[IO.File]::WriteAllText($JsPath, "window._PRODUCT_CATALOG=$json;", (New-Object Text.UTF8Encoding $false))
Write-Host "제품목록.js 업데이트 완료 ($($catalog.Count)개)"

Start-Process $HtmlSrc
Write-Host "브라우저로 열기: $HtmlSrc"

# 심플 캐드 (세라믹 상판 가공비 계산기)

세라믹 상판 도면을 그리고 가공비 견적·도면(PDF)·온장 배치를 만드는 **단일 파일 웹 앱**.
사용자와의 대화·커밋 메시지는 **한국어**.

- 앱: `index.html` 하나(HTML/CSS/JS 모두 인라인, 빌드 없음, 외부 라이브러리 없음)
- 배포: GitHub Pages — https://js80jjang.github.io/simplecad/ (저장소 `js80jjang/simplecad`, **공개**)
- 로컬 실행: `세라믹 심플 캐드 계산기.bat` → `launch.ps1`(엑셀 제품 목록 → `제품목록.js` 생성 후 index.html 열기)

## 저장소에 없는 파일 (PC마다 따로 복사)
- `세라믹제품목록.xlsx`, `제품목록.js` — 제품 목록. 공개 저장소라 `.gitignore`로 제외. 다른 PC에는 USB/클라우드로 복사.
- 고객 도면/견적 파일(.ceramic, .dxf)은 절대 커밋하지 않음.

## 이 PC 환경 (Windows)
- `git`이 PATH에 없음 → GitHub Desktop 내장 git 사용 (버전 폴더는 업데이트마다 바뀜):
  `(Get-ChildItem "$env:LOCALAPPDATA\GitHubDesktop\app-*\resources\app\git\cmd\git.exe" | Sort-Object FullName | Select-Object -Last 1).FullName`
- 명령줄 `git push`는 인증 불가 → **GitHub Desktop의 Push origin**으로 올림. 커밋은 하되 **올리기 전 사용자 확인**.
  저장된 토큰을 꺼내 쓰는 방식은 쓰지 않음.
- Python/Node 없음 → 스크립트는 PowerShell 5.1. 한글이 든 `.ps1`은 **UTF-8 BOM**으로 저장(없으면 깨짐).
- 테스트: 브라우저 패널에서 `file://`로 열면 data: 주소라 localStorage가 막힘 → 저장소/파일 fetch가 필요하면
  `powershell -ExecutionPolicy Bypass -File tools\serve.ps1 [-Dxf 경로]` 후 http://localhost:8765/ 사용.

## 코드 구조 (index.html 안 주요 함수)
- 상태: `shapes`(도형 배열), `nextId`, `products`, 단가 입력칸(`su-/du-/ru-/cu-/xt-` + `TIER_KEYS`)
- 도형 kind: `rect`(x,y,w,h,rotation,cornerType/cornerSize,corners,groupId/groupRole/applianceType,pieceName,shapeNum,hideDims),
  `line`(x1..y2, DXF 곡선 근사면 arcR/arcMid), `circle`(cx,cy,r,holeType: faucet|outlet|cut), `arc`, `ellipse`,
  `grindregion`(밑면연마, inward, depth), `gosramark`(고스라, outward), `dimline`, `jollymark`,
  `note`(도면 글자: x,y,text,fs=도면화 px,color), `arrow`(화살표: x1..y2=촉, bend 휨, color) — 주석이라 조각/가공비/온장 배치에서 제외
- 싱크볼/쿡탑 = `groupRole:'main'` rect (라운드=싱크볼, 직각=쿡탑) + 싱크볼은 둘레 고스라 4개
- 편집 화면: `redraw` → `drawShape`/`drawDims`/`drawNestDims`/`drawShapeNumbers` …
- 판정 공통: `isInsideRect`(회전 포함), `_axisBox`, `_rightAngle`, `findEdgeContext`, `_lineBoundaryGroups`, `_gosraDir`
- 조각/배치: `_collectBoardItems` → `_packBoardItems` / `_restoreSavedBoards`, `showBoardLayout`, `renderBoardLayout`
- 도면화(PDF): `exportDrawingA4` → `_drawCleanExport`(1쪽, `_exp*` 함수들) + `_renderCleanBoards`(2쪽 온장 배치)
  - 겹침 방지: `_pdr`(글자 상자), `_pseg`(그린 선), `_pcut`(타공부 안쪽) 등록 후 `_expDim`/`_expBestDim`/`_expLeader`가 빈 자리 선택
- 가공비: `calcCost` / 저장·불러오기: `_makeProjectData`, `loadProject`(.ceramic=JSON, 단가 포함) / DXF: `importDxf`
- 단가: 브라우저 localStorage(`scd_prices_<등급>`), 다른 PC로는 `exportTierPrices`/`importTierPrices`

## 도면 표기 규칙 (사용자 확정)
- 막힌 모서리 = 실선, **밑면연마 = 노란 굵은 선(50% 투명)**, **고스라 = 빨간 ▲** (꼭지점이 방향)
  - 사각/선 절단 조각 변: 바깥에서 조각 안쪽을 향함 / 싱크볼·쿡탑 변: 타공부 안쪽에서 선을 향함
- 조각마다 색(채움+외곽), 치수는 조각 색 화살표 치수, 정수 표기, 글자는 항상 바로 서게
- R값·Φ값은 대각선 지시선으로 빼서 어떤 선에도 글자가 걸치지 않게
- 조각 자동 번호는 상판 조각만(싱크볼/쿡탑/타공/다른 사각형 안의 사각형 제외)

## DXF 불러오기 해석 규칙 (오토캐드)
- 단위: `$INSUNITS` 따름. 단 인치/피트인데 환산 크기가 30m를 넘으면 mm 도면으로 보고 배율 1 (템플릿 탓에 인치로 저장된 mm 도면이 흔함)
- 폭 있는 폴리선 = 테두리/주석 → 무시 / 블록(INSERT)·글자·치수 무시
- 사각형 끝에서 끝까지 가로지르는 선(가장자리 60mm 초과 안쪽) = **접합부** → 조각 분할
- 변에서 60mm 이내 평행선 = 해치 경계 → 절단선 아님
- 조각 안 사각형: 라운드 → 싱크볼, 직각 → 쿡탑 / φ45 이하 원 → 수전 타공
- **해치 = 밑면연마**, **"OPEN" 글자 = 그 변에 밑면연마 + 고스라**
- 조각 이름: 조각 안(없으면 300mm 이내) 짧은 글자
- 닫힌 폴리선 사각형은 코너마다 라운드/모따기가 달라도 사각 조각(`corners`)으로

## DXF 내보내기 (`buildDxf` / `exportDxf`, 상단 "DXF 내보내기" 버튼)
- 오토캐드 R12(AC1009) ASCII, mm(`$INSUNITS`=4), Y 뒤집기, 한글은 `\U+XXXX`, Φ는 `%%c`
- 레이어: `SC-PIECE` 조각 / `SC-CUTOUT` 싱크볼·쿡탑 / `SC-HOLE` 타공 / `SC-GRIND` 밑면연마 띠 / `SC-GOSRA` 고스라 ▲(SOLID)
  / `SC-DIM` 치수(선+화살촉+글자) / `SC-NAME` 조각 이름 / `SC-NOTE` 도면 글자·화살표 / `SC-JOLLY` 졸리컷
- 다시 불러오기 호환: `SC-DIM/NOTE/GOSRA/JOLLY`는 무시, `SC-GRIND` 띠는 해치처럼(밑면연마+고스라) 해석

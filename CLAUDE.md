# 심플 캐드 (세라믹 상판 가공비 계산기)

세라믹 상판 도면을 그리고 가공비 견적·도면(PDF)·온장 배치를 만드는 **단일 파일 웹 앱**.
사용자와의 대화·커밋 메시지는 **한국어**.

- 앱: `index.html` 하나(HTML/CSS/JS 모두 인라인, 빌드 없음, 외부 라이브러리 없음) + `dxf-form.js`(DXF 기본 양식 데이터)
- 배포: GitHub Pages — https://js80jjang.github.io/simplecad/ (저장소 `js80jjang/simplecad`, **공개**)
- 로컬 실행: `세라믹 심플 캐드 계산기.bat` → `launch.ps1`(엑셀 제품 목록 → `제품목록.js` 생성 후 index.html 열기)

## 윤현몰 제품 목록 (`mall-catalog.js`, 자동 생성 — 직접 고치지 않음)
- `.github/workflows/mall-catalog.yml`이 매일 03:00(KST) `tools/update_mall_catalog.py` 실행 → 바뀌었으면 봇이 커밋·푸시
  → 로컬 작업 전 pull 필수(봇 커밋이 생김). 손으로 돌리기: Actions → "윤현몰 제품 목록 갱신" → Run workflow
- 가져오는 분류: 스크립트의 `CATEGORIES`(지금 `009003` = 두께 12mm, `009001` = 두께 6mm). 고도몰 목록 HTML(`item_cont`/`item_name`/`item_name_explain`/`item_price`/`m2`)을 읽음
  — 쇼핑몰 화면이 바뀌어 10개 미만이면 실패로 끝나고 기존 파일 유지
- 항목: `{id,name(한글),en,size(1600×3200×12T),price(장당),m2,img,url,cate}`. 앱의 `_catalog` = 몰 + 엑셀(`제품목록.js`), 이름+사이즈로 중복 제거
  — 검색은 한글·영문·사이즈, 여러 단어는 모두 포함. 고르면 제품명·사이즈 채움 + 온장 크기(`board-w`=긴 쪽, `board-h`)도 그 사이즈로(`_setBoardFromSize`)

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
- 작업 정보 줄(도면 위 `#work-bar`): `company-name`(업체명), `site-addr`(주소), 제품(`renderProductList`, 2개부터 `#prod-pop`),
  `deliv-date`/`deliv-time`(직접 입력 → `_normDate` 2026.10.28 / `_normTime` 14:00). 업체명·주소 최근 15개는 localStorage
  — 도면화·DXF에는 `_companySite()`("업체명 - 주소"), 저장 파일 이름은 `_saveBaseName()`(업체명-주소-20261021), 기본 위치 바탕화면
- 도형 kind: `rect`(x,y,w,h,rotation,cornerType/cornerSize,corners,groupId/groupRole/applianceType,pieceName,shapeNum,hideDims),
  `line`(x1..y2, DXF 곡선 근사면 arcR/arcMid), `circle`(cx,cy,r,holeType: faucet|outlet|cut), `arc`, `ellipse`,
  `grindregion`(밑면연마, inward, depth), `gosramark`(고스라, outward), `dimline`, `jollymark`,
  `note`(도면 글자: x,y,text,fs=도면화 px,color), `arrow`(화살표: x1..y2=촉, bend 휨, color — 그린 뒤 양 끝 점 끌기/길이 입력으로 크기 수정), `linkmark`(연결 표시: x1..y2 따라 물결 2줄, color) — 주석이라 조각/가공비/온장 배치에서 제외
- 싱크볼/쿡탑 = `groupRole:'main'` rect (라운드=싱크볼, 직각=쿡탑) + 싱크볼은 둘레 고스라 4개
- 편집 화면: `redraw` → `drawShape`/`drawDims`/`drawNestDims`/`drawShapeNumbers` …
- 선 절단 도구 = 오토캐드 LINE 방식(`lineChain`, `_lineAddTo/_lineMouseUp/_lineKey/_lineOverlay`): 시작점에서 드래그=방향 고정(`dir`), 놓으면 길이·각도 입력란(`#line-pop`, `_linePopShow`; `line-ang`는 드래그 방향으로 미리 채움, 0°=오른쪽 반시계, Tab=칸 이동) →
  숫자+Enter=그 방향으로 길이(놓기만 해서는 안 그림 — 전역 mouseup의 `finalizeShape`는 line 제외), 끝나도 도구 유지, 다음 선은 방향 쪽을 클릭(드래그도 됨)하면 입력란, 스냅점(끝점·중간점·교차점 등, 격자 제외) 클릭은 입력 없이 그 점까지(`lineDown.snap`)(입력란에서 빈 Enter=끝·C=닫기·U=취소), 끝점에서 다시 드래그 → 숫자… 이어 그리기, 드래그 없는 클릭=그 점까지,
  `300,-200`(상대, 위가 +)·`500<90`(길이<각도), 빈 Enter/Esc/오른쪽 클릭=끝, C=닫기, U=마지막 선 취소. 기본 직교(Shift=자유)
- 판정 공통: `isInsideRect`(회전 포함), `_axisBox`, `_rightAngle`, `findEdgeContext`, `_lineBoundaryGroups`, `_gosraDir`
- 조각/배치: `_collectBoardItems` → `_packBoardItems` / `_restoreSavedBoards`, `showBoardLayout`, `renderBoardLayout`
  - 온장 배치 창: 오른쪽 클릭 = 90° 돌리기(`p.rotated`), Shift+오른쪽 클릭 = 선 조각만 각도 입력(그린 방향 0°, 반시계 +) → `item.rot`,
    저장 배치에 `rot` 기록(`_rotBox`로 상자 다시 계산해 복원)
  - 선 조각이 그대로 온장에 안 들어가면 변 하나를 가로로 눕힌 각도 중 들어가는(면적 최소) 것으로 돌림(`item.rot/rx0/ry0`, `_boardPiece`의 `M`이 적용)
- 도면화(PDF): `exportDrawingA4` → `_drawCleanExport`(1쪽, `_exp*` 함수들) + `_renderCleanBoards`(2쪽 온장 배치)
  - 겹침 방지: `_pdr`(글자 상자), `_pseg`(그린 선), `_pcut`(타공부 안쪽) 등록 후 `_expDim`/`_expBestDim`/`_expLeader`가 빈 자리 선택
- 가공비: `calcCost` / 저장·불러오기: `_makeProjectData`, `loadProject`(.ceramic=JSON, 단가 포함) / DXF: `importDxf`
- 단가: 브라우저 localStorage(`scd_prices_<등급>`), 다른 PC로는 `exportTierPrices`/`importTierPrices`

## 도면 표기 규칙 (사용자 확정)
- 막힌 모서리 = 실선, **밑면연마 = 노란 굵은 선(50% 투명)**, **고스라 = 빨간 ▲** (꼭지점이 방향)
  - 사각/선 절단 조각 변: 바깥에서 조각 안쪽을 향함 / 싱크볼·쿡탑 변: 타공부 안쪽에서 선을 향함
- 조각마다 색(채움+외곽), 치수는 조각 색 화살표 치수, 정수 표기, 글자는 항상 바로 서게
- 선 각도(`_lineAngleMarks` → `_drawAngleMarks`, 편집 화면·도면화 공통, DXF는 `_dxfCollect`에서 SC-DIM ARC+TEXT, ° = `%%d`): 선 두 개가 만나는 점마다 사잇각 호+값(직각·일직선 제외),
  이어진 선이 없는 비스듬한 선은 시작점에서 수평 점선 기준 각도
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

## DXF 내보내기 (`exportDxf` 창 → `buildDxf` / `buildDxfInForm`, 상단 "DXF 내보내기" 버튼)
- 도형 → 추상 엔티티 `_dxfCollect(H)` → `_dxfWriteEnts`(R12 또는 R2000+ 핸들 형식). mm, Y 뒤집기, 한글 `\U+XXXX`, Φ `%%c`, 글자 스타일 `SC-KOR`(malgun.ttf)
- 양식 없이: R12(AC1009) ASCII
- "DXF 내보내기" 버튼 = 묻지 않고 양식에 넣어서(`buildDxfInForm`). 옆 ⚙ = 양식 바꾸기 / 기본으로 되돌리기 / 양식 없이
- 기본 양식: `dxf-form.js`(`window._DXF_DEFAULT_FORM`) = (주)윤현상재 가공의뢰서 DXF (사용자 승인으로 공개 저장소에 포함,
  드라이브 경로는 모두 파일 이름만, 옛 양식 블록의 담당자 이름은 비움). 원본 `윤현상재_가공의뢰서.dxf`가 바뀌면 다시 만들어야 함
  - 현재 양식(2026-10 개정, 블록 `FORM`, 영문 표제란): 모형 공간에 놓인 ATTDEF(도면명(한줄)·축척A3·도면번호)는 블록 안에서
    안 보이므로 TEXT로 바꿔 채움(도면명=제품명, 축척=1/N, 도면번호는 그대로), 왼쪽 위 "업체명 - 현장주소 / 제품명 - 장수 / 사이즈"
    MTEXT는 현장 주소·제품명-장수·사이즈로, DRAWN / DATE 칸에 오늘 날짜. 도면은 위·아래 양식 글자를 피해서 배치
  - 옛 양식(한글 표제란: 도면명·축척·납품일정·납품장소) 채우기도 그대로 지원
  — ⚙로 고른 다른 양식(R2000+, `$HANDSEED` 필요)은 이 PC 브라우저 localStorage(`scd_dxf_template`)에만 저장되고 기본보다 우선
  - 양식의 모형 공간 내용 전체를 블록 `SC_FORM`으로 옮기고(소유자 330만 교체) INSERT로 축척만큼 키움 → 도면은 1:1 mm
  - 테두리 블록 = 표제란 글자(도면명·축척·납품일정·납품장소…)가 든 블록. 굵은 폴리선으로 안쪽 테두리·표제란 경계를 찾음
  - 축척: 테두리 폭=A3 420mm 기준, 1/5·1/10·1/15·1/20… 중 치수 포함 도면이 들어가는 가장 작은 값. 치수 글자 = 범례 글자(40)×배율
  - 표제란 채움(레이어 `SC-TITLE`): 도면명=제품명, 축척=A3 1/N, 납품일정=출고 예정일, 납품장소=현장 주소
  - 검증: ezdxf(`python -m pip install --user ezdxf matplotlib`)로 recover/audit + PNG 렌더 (앱에는 안 씀)
- 치수(도면화와 같은 규칙): 조각 W/H, 선 절단 선 길이(`_lineOutwardSide`로 바깥쪽, 곡선 근사 선분은 R값만), 싱크볼·쿡탑 W/H + 가까운 좌/우·위/아래 조각 변까지 위치, R·C값 지시선,
  수전 → 가장 가까운 싱크볼 변(같은 줄 여러 개는 이어서 간격), 콘센트 등 → 가까운 선, Φ값은 치수 없는 쪽 지시선
- 레이어: `SC-PIECE` 조각 / `SC-CUTOUT` 싱크볼·쿡탑 / `SC-HOLE` 타공 / `SC-GRIND` 밑면연마 띠+45° 빗금 / `SC-GOSRA` 고스라 ▲
  / `SC-DIM` 치수(선+화살촉+글자) / `SC-NAME` 조각 이름 / `SC-NOTE` 도면 글자·화살표 / `SC-JOLLY` 졸리컷 ★ / `SC-TITLE` 표제란
- 다시 불러오기 호환: `SC-DIM/NOTE/GOSRA/JOLLY/TITLE`은 무시, `SC-GRIND` 띠는 해치처럼(밑면연마+고스라) 해석, 양식 블록(INSERT)은 무시

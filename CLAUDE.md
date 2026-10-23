# 심플 캐드 (세라믹 상판 가공비 계산기)

세라믹 상판 도면을 그리고 가공비 견적·도면(PDF)·온장 배치를 만드는 **단일 파일 웹 앱**.
사용자와의 대화·커밋 메시지는 **한국어**.

- 앱: `index.html` 하나(HTML/CSS/JS 모두 인라인, 빌드 없음, 외부 라이브러리 없음) + `dxf-form.js`(DXF 기본 양식 데이터)
- 배포: GitHub Pages — https://js80jjang.github.io/simplecad/ (저장소 `js80jjang/simplecad`, **공개**)
- 앱 설치(PWA): `manifest.webmanifest` + `sw.js`(서비스 워커) + `icons/`. GitHub Pages 주소에서 크롬/엣지 "앱 설치"(툴바 `#btn-install`,
  `beforeinstallprompt` 때만 보임) → 별도 창 앱. sw.js는 앱 파일 "네트워크 먼저"(온라인이면 항상 최신, 오프라인이면 저장본),
  `mall-img/`는 저장본 먼저, 다른 사이트(Firebase 등) 요청은 안 건드림. file://에선 등록 안 함. 브라우저 패널은 서비스 워커 미지원 → 확인은 실제 크롬에서
  - 아이콘은 Pillow 스크립트로 만든 것(상판·싱크볼·수전·절단선). 바꾸려면 PNG 4개(192/512/maskable-512/apple-touch 180) 교체
- 패치 노트: `patch-notes.js`(`window._PATCH_NOTES`, 맨 위가 최신 `{v:'날짜', groups:[{t,items}]}`). 앱을 열 때 안 본 버전이 있으면 팝업
  (`showPatchNotes`, 본 버전 `scd_patch_seen`), 도구줄 "📢 새 소식"으로 전체 보기. **사용자에게 보이는 변경을 올릴 때 맨 위에 새 버전 추가**
- 로컬 실행: `세라믹 심플 캐드 계산기.bat` → `launch.ps1`(엑셀 제품 목록 → `제품목록.js` 생성 후 index.html 열기)

## 윤현몰 제품 목록 (`mall-catalog.js`, 자동 생성 — 직접 고치지 않음)
- `.github/workflows/mall-catalog.yml`이 매일 03:00(KST) `tools/update_mall_catalog.py` 실행 → 바뀌었으면 봇이 커밋·푸시
  → 로컬 작업 전 pull 필수(봇 커밋이 생김). 손으로 돌리기: Actions → "윤현몰 제품 목록 갱신" → Run workflow
- 가져오는 분류: 스크립트의 `CATEGORIES`(지금 `009003` = 두께 12mm, `009001` = 두께 6mm). 고도몰 목록 HTML(`item_cont`/`item_name`/`item_name_explain`/`item_price`/`m2`)을 읽음
  — 쇼핑몰 화면이 바뀌어 10개 미만이면 실패로 끝나고 기존 파일 유지
- 항목: `{id,name(한글),en,size(1600×3200×12T),price(장당),m2,img,url,cate}`. 앱의 `_catalog` = 몰 + 엑셀(`제품목록.js`), 이름+사이즈로 중복 제거
  — 검색은 한글·영문·사이즈, 여러 단어는 모두 포함. 고르면 제품명·사이즈 채움 + 온장 크기(`board-w`=긴 쪽, `board-h`)도 그 사이즈로(`_setBoardFromSize`)

- 온장 이미지: 같은 워크플로가 `tools/update_mall_images.py`(Pillow) 실행 → 몰 목록 이미지(= 온장 전체 사진 2:1, 몰에서 가장 큰 것이 1150×576)를 줄이지 않고 JPEG q86(`SPEC`, 바꾸면 전부 다시 받음, 장당 ≈90KB)으로
  `mall-img/<상품번호>.js`(`window._MALL_IMG[id]=data URL`)로 저장, `mall-img/manifest.json`에 원본 주소(같으면 다시 안 받음), 빠진 제품은 지움
  — 쇼핑몰 이미지 서버에 CORS가 없어 바로 연결하면 도면화 캔버스가 막히므로 저장소에 받아 둠(사용자 승인: 공개 저장소에 올려도 됨)
  - 앱: `_slabImgFor(제품 이름)`이 `<script>`로 불러옴(`_updateBoardQty`에서 미리), `_boardLabel(장)`=조각에 붙인 제품/첫 제품,
    `_drawSlab`로 온장 배치 창·도면화 2쪽에 채움 — 사진은 실제 밝기 그대로(옅게 하지 않음), 남는 부분만 검정 32%로 어둡게,
    조각은 배치된 자리 무늬 그대로 + 조각 색 외곽선. 이미지 없으면 예전 색
  - 테스트는 http(serve) 주소로 — 브라우저 패널의 data: 주소에서는 `mall-img/` 상대 경로를 못 읽음

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
- 제품: 작업 정보 줄에 제품마다 한 줄씩 아래로(`renderProductList`, 마지막 줄 "+ 제품"). 제품 색 = 순서대로 `_prodColor(i)`(`_PCOLS`)
  - **도형마다 제품**(`s.label`=제품 이름, 안 정하면 첫 제품 — `_shapeProdIdx`/`_itemProd`): 도형 선택 → 제품 줄 앞 ●(`assignProduct`).
    그룹(싱크볼 등)·이어진 선 조각 전체가 같이 바뀜, 지정하면 저장된 온장 배치는 초기화. 제품 이름 바꾸면 도형도 따라감(`_setProdName`), 제품 빼면 첫 제품으로
  - 편집 화면: 제품 2개 이상이면 조각을 제품 색으로 옅게 + 왼쪽 아래 제품명(`_drawProdTints`), ●에 마우스 올리면 그 제품만 진하게(`_hoverProd`). 도형 속성창의 제품 선택은 없앰
  - 온장 배치: 제품별로 장을 따로(`_packBoardItems` 그룹 = `_itemProd`), 장 머리글 `_boardTitle`="온장 N · 제품명", 온장 사진도 그 제품(`_boardLabel`).
    **온장 크기도 제품마다**: 제품 사이즈 칸에서(`_prodBoardSize`, 없으면 도구줄 온장 칸) → 장마다 `board.bw/bh`(`_boardDims`),
    배치 창·도면화 2쪽 칸은 가장 큰 온장 기준·장은 자기 크기로, 끌기·돌리기 한계는 그 장 유효 영역(`_bsArea`). 저장 배치는 `sig`(`_boardSizeSig`)가 같을 때만 복원
    도면화 1쪽 왼쪽 위·DXF 양식 글자는 제품마다 한 줄
- **온장 그대로 사이즈**(`_fullBoardFit(s,w,h)`, `_FULL_TXT`): 사각 조각 한 변 = 그 제품 온장 폭/길이(다른 변은 온장 안)면
  배치 칸은 그 방향 20(여백 양쪽) 줄여 넣고(`item.fw/fh`) `_boardPiece`가 온장 끝까지 늘려 그림, `calcCost` 사각 절단에서 그 방향 양쪽 면 길이 뺌,
  도면화·DXF 치수와 온장 배치 크기 글자 옆에 "온장 그대로 사이즈" (편집 화면 치수는 그대로)
- 제품 수량 = 온장 배치 장수(자동, 읽기 전용 `pq-N`): `_updateBoardQty`(calcCost 끝에서 `_scheduleBoardQty`, 배치 창 닫을 때)가
  손으로 고친 배치(`_savedBoardLayout`)나 자동 배치에서 장마다 고른 제품별로 셈. **가공비에 곱하지 않음**(가공을 여러 번 하는 뜻 아님)
- 작업 정보 줄(도면 위 `#work-bar`): `site-info` 한 칸 "업체명/현장주소"(첫 '/' 앞=업체명, 뒤=주소, `_syncSiteInfo`/`_setSiteInfo`) →
  숨은 `company-name`(업체명)·`site-addr`(주소)에 나눠 넣음(저장 파일 company/siteAddr 그대로), 최근 목록 `scd_siteinfo_history`, 제품(`renderProductList`, 2개부터 `#prod-pop`),
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
- 트림 `doTrim`: rect는 `_trimRectGeo`(90° 단위 회전 = 보이는 대로 회전 없는 rect·코너 키 돌림, 그 밖 각도 = 꼭짓점 `_pts`) +
  `_trimRectEdges`(위→오른쪽→아래→왼쪽, 클릭 판정·교점·분해가 같은 방향)로. 잘린 구간에 겹친 같은 직선 위 선은 `_trimOverlaps`로 같이 지움
- 조각/배치: `_collectBoardItems` → `_packBoardItems` / `_restoreSavedBoards`, `showBoardLayout`, `renderBoardLayout`
  - 조각 = 다른 사각형·닫힌 선 조각 안에 들지 않은 rect/원 + 이어진 선 그룹. 돌린 rect는 회전 포함 상자 크기(`getBBox`)로, 그리기(`_expRectPathLocal`)도 회전 포함
  - 온장 배치 창: 오른쪽 클릭 = 90° 돌리기(`p.rotated`), Shift+오른쪽 클릭 = 선 조각만 각도 입력(그린 방향 0°, 반시계 +) → `item.rot`,
    저장 배치에 `rot` 기록(`_rotBox`로 상자 다시 계산해 복원)
  - 조각이 작아 안에 크기 글자가 안 들어가면 빈 곳에 글자 + 조각을 가리키는 화살표(`_boardPiece`, `tex.board`/`tex._used`):
    온장 안을 훑어 다른 조각·다른 바깥 글자와 안 겹치고 화살표가 다른 조각을 지나지 않는 자리, 없으면 캔버스 안(잘리지 않게).
    번호 칸도 안 들어가는 조각은 바깥 글자 앞에 번호 칸(`_pn`)을 붙임
  - 선 조각이 그대로 온장에 안 들어가면 변 하나를 가로로 눕힌 각도 중 들어가는(면적 최소) 것으로 돌림(`item.rot/rx0/ry0`, `_boardPiece`의 `M`이 적용)
- 도면화(PDF): `exportDrawingA4` → `_drawCleanExport`(도면 쪽, `_exp*` 함수들) + `_renderCleanBoards`(마지막 쪽 온장 배치)
  - 온장 2장 이상이면 도면을 **온장마다 한 쪽**: `_drawingBoards`(저장 배치/자동 배치) → `_shapePieceMap`(도형 → 속한 조각: 조각 안·변 위 → 가장 작은 조각,
    밖이면 가장 가까운 조각, 그룹은 main 자리) → 쪽마다 `shapes`를 그 장 조각 것만으로 잠시 바꿔 `_renderDrawingImage`.
    이때 `_compactPageShapes`가 조각(+딸린 도형)을 원래 자리 대신 줄 맞춰 모은 복사본으로 바꿈(줄 폭을 바꿔 가며 도면 영역 `_DRW_AW×_DRW_AH`에 가장 크게, 간격 = 150px 상당 mm). 배치 안 된 조각은 따로 한 쪽.
    조각 번호는 `_autoPieceNums`를 `shapeNum`에 잠시 고정해 전체 기준 유지. 도면 쪽은 **항상 가로 A4**(`isPort=false`)
  - 밑면연마 띠는 50mm, 단 깊이가 더 큰 것(150×150 원클릭)은 그 깊이로·방향은 저장된 `inward`(가로선 +y, 세로선 +x)
  - 선 조각 가로/세로 선 치수는 `_lineDimPlan`으로 조각 상자 바깥 치수 줄(위·아래·왼·오)에 맞춤, 같은 쪽 범위가 겹치면 짧은 것부터 안쪽 줄 (DXF도 같음)
  - `_expDim`: 30px 미만 짧은 치수는 화살표를 바깥에서 안쪽으로, 글자는 화살표 너머
  - 범례는 가공이 없어도 항상: 실선 = 닫힘면, 주황 빗금 = 밑면연마(50mm), 검정 ▲ = 고스라, 빨간 ★ = 졸리컷
  - 겹침 방지: `_pdr`(글자 상자), `_pseg`(그린 선), `_pcut`(타공부 안쪽) 등록 후 `_expDim`/`_expBestDim`/`_expLeader`가 빈 자리 선택
- 가공비: `calcCost` / 저장·불러오기: `_makeProjectData`, `loadProject`(.ceramic=JSON, 단가 포함) / DXF: `importDxf`
- 단가: 브라우저 localStorage(`scd_prices_<등급>`), 다른 PC로는 `exportTierPrices`/`importTierPrices`

## 도면 표기 규칙 (사용자 확정)
- (도면화·온장 배치) 변은 모두 조각 색 실선, **밑면연마 = 변에서 재료 쪽 50mm 띠에 주황 45° 빗금**(`_expHatchBand`, `_GRIND_MM`),
  **고스라 = 검정 ▲** (꼭지점이 방향), **졸리컷 = 빨간 ★·선** — 편집 화면은 예전 색 그대로(고스라 빨강, 졸리컷 파랑)
  - 사각/선 절단 조각 변: 바깥에서 조각 안쪽을 향함 / 싱크볼·쿡탑 변: 타공부 안쪽에서 선을 향함 (밑면연마 띠 방향도 같음, `_gosraDir`)
- 조각마다 색은 **외곽선만**(안은 흰색, 음영 없음 — 도면화 1쪽·온장 배치 사진 없을 때), 치수는 조각 색 화살표 치수, 정수 표기, 글자는 항상 바로 서게
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

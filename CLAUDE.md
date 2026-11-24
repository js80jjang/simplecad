# 심플 캐드 (세라믹 상판 가공비 계산기)

세라믹 상판 도면을 그리고 가공비 견적·도면(PDF)·원판 배치를 만드는 **단일 파일 웹 앱**.
사용자와의 대화·커밋 메시지는 **한국어**.

- 앱: `index.html` 하나(HTML/CSS/JS 모두 인라인, 빌드 없음, 외부 라이브러리 없음) + `dxf-form.js`(DXF 기본 양식 데이터)
- 배포: GitHub Pages — https://js80jjang.github.io/simplecad/ (저장소 `js80jjang/simplecad`, **공개**)
- 앱 설치(PWA): `manifest.webmanifest` + `sw.js`(서비스 워커) + `icons/`. GitHub Pages 주소에서 크롬/엣지 "앱 설치"(툴바 `#btn-install`,
  `beforeinstallprompt` 때만 보임) → 별도 창 앱. sw.js는 앱 파일 "네트워크 먼저"(온라인이면 항상 최신, 오프라인이면 저장본),
  `mall-img/`는 저장본 먼저, 다른 사이트(Firebase 등) 요청은 안 건드림. file://에선 등록 안 함. 브라우저 패널은 서비스 워커 미지원 → 확인은 실제 크롬에서
  - 아이콘 = 사용자가 준 로고 PNG(512, 둥근 사각형·ㄱ자 상판·치수·연필, 2026-10-26)를 PowerShell System.Drawing으로 줄인 것. 192/512는 투명 모서리 그대로,
    apple-touch 180·maskable-512는 네이비 그라데이션 바탕(maskable은 로고 94%). 바꾸려면 PNG 4개 교체 + manifest·index.html·sw.js의 `?v=N`을 올리고 sw.js `CACHE` 버전도 올림
    (주소가 같으면 크롬이 예전 아이콘을 다시 씀). 바탕화면 아이콘은 윈도우 아이콘 캐시 때문에 다시 설치 후에도 남을 수 있음 → `ie4uinit.exe -show` 또는 재부팅. 머리글 로고는 같은 그림의 SVG(index.html 안)
- 패치 노트: `patch-notes.js`(`window._PATCH_NOTES`, 맨 위가 최신 `{v:'날짜', groups:[{t,items}]}`). 앱을 열 때 안 본 버전이 있으면 팝업
  (`showPatchNotes`, 본 버전 `scd_patch_seen`), 도구줄 "📢 새 소식"으로 전체 보기. **사용자에게 보이는 변경을 올릴 때 맨 위에 새 버전 추가**
- 로컬 실행: `세라믹 심플 캐드 계산기.bat` → `launch.ps1`(index.html 열기만). 제품 목록은 윤현몰(`mall-catalog.js`)만 씀 — 엑셀 목록 기능은 없앰

## 윤현몰 제품 목록 (`mall-catalog.js`, 자동 생성 — 직접 고치지 않음)
- `.github/workflows/mall-catalog.yml`이 매일 03:00(KST) `tools/update_mall_catalog.py` 실행 → 바뀌었으면 봇이 커밋·푸시
  → 로컬 작업 전 pull 필수(봇 커밋이 생김). 손으로 돌리기: Actions → "윤현몰 제품 목록 갱신" → Run workflow
- 가져오는 분류: 스크립트의 `CATEGORIES`(지금 `009003` = 두께 12mm, `009001` = 두께 6mm). 고도몰 목록 HTML(`item_cont`/`item_name`/`item_name_explain`/`item_price`/`m2`)을 읽음
  — 쇼핑몰 화면이 바뀌어 10개 미만이면 실패로 끝나고 기존 파일 유지
- 항목: `{id,name(한글),en,size(1600×3200×12T),price(장당),m2,img,url,cate}`. 앱의 `_catalog` = 몰 상품만, 이름+사이즈로 중복 제거
  — 검색은 한글·영문·사이즈, 여러 단어는 모두 포함. 고르면 제품명·사이즈 채움 + 원판 크기(`board-w`=긴 쪽, `board-h`)도 그 사이즈로(`_setBoardFromSize`)

- 원판 이미지: 같은 워크플로가 `tools/update_mall_images.py`(Pillow) 실행 → 몰 목록 이미지(= 원판 전체 사진 2:1, 몰에서 가장 큰 것이 1150×576)를 줄이지 않고 JPEG q86(`SPEC`, 바꾸면 전부 다시 받음, 장당 ≈90KB)으로
  `mall-img/<상품번호>.js`(`window._MALL_IMG[id]=data URL`)로 저장, `mall-img/manifest.json`에 원본 주소(같으면 다시 안 받음), 빠진 제품은 지움
  — 목록 이미지 폭이 600 미만(6mm 제품은 몰 목록 이미지가 150×75)이면 상품 페이지의 상세 이미지(`/image/detail/`, 대부분 1150×576, 비율 1.6~2.4일 때만)를 씀,
    manifest 값 끝 `|d` = 상세 이미지 확인함(다시 안 봄). mall-img 이미지가 바뀌면 sw.js `CACHE` 버전도 올림(설치 앱은 mall-img를 저장본 먼저 씀)
  — 쇼핑몰 이미지 서버에 CORS가 없어 바로 연결하면 도면화 캔버스가 막히므로 저장소에 받아 둠(사용자 승인: 공개 저장소에 올려도 됨)
  - 앱: `_slabImgFor(제품 이름)`이 `<script>`로 불러옴(`_updateBoardQty`에서 미리), `_boardLabel(장)`=조각에 붙인 제품/첫 제품,
    `_drawSlab`로 원판 배치 창·도면화 2쪽에 채움 — 사진은 실제 밝기 그대로(옅게 하지 않음), 남는 부분만 검정 32%로 어둡게,
    조각은 배치된 자리 무늬 그대로 + 조각 색 외곽선. 이미지 없으면 예전 색
  - 테스트는 http(serve) 주소로 — 브라우저 패널의 data: 주소에서는 `mall-img/` 상대 경로를 못 읽음

## 저장소에 올리지 않는 파일
- 고객 도면/견적 파일(.ceramic, .dxf)은 절대 커밋하지 않음. 단가 파일(`단가설정_*.json`, 원가 포함)도 `.gitignore`.
- 예전 엑셀 제품 목록(`*.xlsx`, `제품목록.js`)은 더 이상 쓰지 않지만 남아 있어도 올라가지 않게 `.gitignore`에 둠.

## 이 PC 환경 (Windows)
- `git`이 PATH에 없음 → GitHub Desktop 내장 git 사용 (버전 폴더는 업데이트마다 바뀜):
  `(Get-ChildItem "$env:LOCALAPPDATA\GitHubDesktop\app-*\resources\app\git\cmd\git.exe" | Sort-Object FullName | Select-Object -Last 1).FullName`
- 명령줄 `git push`는 인증 불가 → **GitHub Desktop의 Push origin**으로 올림. 커밋은 하되 **올리기 전 사용자 확인**.
  저장된 토큰을 꺼내 쓰는 방식은 쓰지 않음.
- Python/Node 없음 → 스크립트는 PowerShell 5.1. 한글이 든 `.ps1`은 **UTF-8 BOM**으로 저장(없으면 깨짐).
- 테스트: 브라우저 패널에서 `file://`로 열면 data: 주소라 localStorage가 막힘 → 저장소/파일 fetch가 필요하면
  `powershell -ExecutionPolicy Bypass -File tools\serve.ps1 [-Dxf 경로]` 후 http://localhost:8765/ 사용.

## 화면 디자인 (2안 "미드나잇 골드", 2026-10-26 사용자 확정)
- 바탕 #060B16 / 패널 #0A1222 / 입력칸·호버 #121D33 / 테두리 #1C2A47 / 버튼 #16233D / 선택·주버튼 #1F3F7A(테두리 #2A4F92)
  / 강조(제목·값) 금색 #E3B861(밝은 #F1D69A) / 글자 #D9DFEA, 흐린 글자 #A9B4C8·#75839C·#56647E. 글꼴 나눔스퀘어(없으면 맑은 고딕)
- 새 화면 요소도 이 색을 쓰기 (예전 파랑 #1565C0·#263545·#90CAF9 계열은 모두 바꿈). CSS 끝 "네이비 테마 2안" 묶음이 덮어쓰는 규칙, 머리글 = SVG 로고 + `.hd-name`

## 코드 구조 (index.html 안 주요 함수)
- 상태: `shapes`(도형 배열), `nextId`, `products`, 단가 입력칸(`su-/du-/ru-/cu-/xt-` + `TIER_KEYS`)
- 제품: 작업 정보 줄에 제품마다 한 줄씩 아래로(`renderProductList`, 마지막 줄 "+ 제품"). 제품 색 = 순서대로 `_prodColor(i)`(`_PCOLS`)
  - 제품 구분 이름 `_prodNames()` = 제품명, 같은 이름이 둘 이상이면 "제품명 (사이즈)"(사이즈도 같으면 ` #번호`). 구분 이름이 바뀌면(이름·사이즈 수정, 제품 추가·삭제)
    `_prodKeyWas`(WeakMap)로 알아채 도형 `s.label`·저장 배치 `boardProds`를 옮김. 이름으로 제품 찾기는 `_prodIdxOf/_prodOf`(예전 파일의 제품명도 첫 같은 이름으로)
  - **도형마다 제품**(`s.label`=제품 구분 이름, 안 정하면 첫 제품 — `_shapeProdIdx`/`_itemProd`): 도형 선택 → 제품 줄 앞 ●(`assignProduct`).
    그룹(싱크볼 등)·이어진 선 조각 전체가 같이 바뀜, 지정하면 저장된 원판 배치는 초기화. 제품 이름 바꾸면 도형도 따라감(`_setProdName`), 제품 빼면 첫 제품으로
  - 편집 화면: 제품 2개 이상이면 조각을 제품 색으로 옅게 + 왼쪽 아래 제품명(`_drawProdTints`), ●에 마우스 올리면 그 제품만 진하게(`_hoverProd`). 도형 속성창의 제품 선택은 없앰
  - 원판 배치: 제품별로 장을 따로(`_packBoardItems` 그룹 = `_itemProd`), 장 머리글 `_boardTitle`="원판 N · 제품명", 원판 사진도 그 제품(`_boardLabel`).
    **원판 크기도 제품마다**: 제품 사이즈 칸에서(`_prodBoardSize`, 없으면 도구줄 원판 칸) → 장마다 `board.bw/bh`(`_boardDims`),
    배치 창·도면화 2쪽 칸은 가장 큰 원판 기준·장은 자기 크기로, 끌기·돌리기 한계는 그 장 유효 영역(`_bsArea`). 저장 배치는 `sig`(`_boardSizeSig`)가 같을 때만 복원
    도면화 1쪽 왼쪽 위·DXF 양식 글자는 제품마다 한 줄
- **원판 그대로 사이즈**(`_FULL_TXT`, 2026-10-27 사용자 확정 "배치 방향 기준"): 사각 조각 한 변이 원판 폭/길이와 같으면 후보(`_fullElig` → `item.full`, w/h는 실제 크기),
  **원판 배치에서 그 변을 원판의 같은 방향으로 놓았을 때만**(1600×3200 원판에 1600 변을 1600 방향으로) 원판 그대로 — 3200 방향으로 놓으면 보통 조각.
  `_placeDims(it,rotated,ew,eh)` = 배치 칸(그 방향은 ew/eh로 20 줄임, 자동 배치·오른쪽 클릭 돌리기·복원이 씀), `_pFull(p)` = 칸이 실제보다 작은 방향, `_pLabel(p)` = 크기 글자+표기.
  `_boardPiece`·`_3dWorldToBoard`가 그 방향 원판 끝까지 늘려 그림. `_fullBoardFit(s)` = 지금 배치(`_drawingBoards`)에서 도형 화면 상자 w/h 기준(캐시: calcCost마다 `_fullVer++`·저장 배치 바뀌면),
  `calcCost` 사각 절단에서 그 방향 양쪽 면 뺌, 도면화·DXF 치수 옆 표기 (편집 화면 치수는 그대로). 배치 창 닫으면 calcCost.
  자동 배치는 실제 크기로만 놓은 쪽이 장수가 적으면 그쪽(`_packBoardItems`). 예전 저장 배치(방향 상관없이 줄인 칸)는 같은 자리에 지금 규칙 크기로 복원, 겹치면 새로 배치
- 제품 수량 = 원판 배치 장수(자동, 읽기 전용 `pq-N`): `_updateBoardQty`(calcCost 끝에서 `_scheduleBoardQty`, 배치 창 닫을 때)가
  손으로 고친 배치(`_savedBoardLayout`)나 자동 배치에서 장마다 고른 제품별로 셈. **가공비에 곱하지 않음**(가공을 여러 번 하는 뜻 아님)
- 작업 정보 줄(도면 위 `#work-bar`): `site-info` 한 칸 "업체명/현장주소"(첫 '/' 앞=업체명, 뒤=주소, `_syncSiteInfo`/`_setSiteInfo`) →
  숨은 `company-name`(업체명)·`site-addr`(주소)에 나눠 넣음(저장 파일 company/siteAddr 그대로), 최근 목록 `scd_siteinfo_history`, 제품(`renderProductList`, 2개부터 `#prod-pop`),
  `deliv-date`/`deliv-time`(직접 입력 → `_normDate` 2026.10.28 / `_normTime` 14:00). 업체명·주소 최근 15개는 localStorage
  — 도면화·DXF에는 `_companySite()`("업체명 - 주소"), 저장 파일 이름은 `_saveBaseName()`(업체명-주소-20261021) — .ceramic·DXF(`_doExportDxf`)·도면화 PDF(인쇄 창 `<title>` = 크롬 PDF 파일 이름)·3D PNG(-3D) 모두 이 이름
  — 저장 창 `_pickSaveFile(kind,기본위치,opts)`: 처음은 바탕화면(.ceramic)/문서(DXF), 그다음은 지난번 저장 파일 핸들(IndexedDB `scd-files`, kind별)의 폴더 + picker `id`.
    불러오기 `loadProject`도 `showOpenFilePicker`로 지난번 불러온 폴더('open', 없으면 'save' → 바탕화면), 없는 브라우저는 파일 칸 → `_loadProjectFile(file,핸들)`
  — "💾 저장"(`saveProject`, `#btn-save`, Ctrl+S) = 지금 파일 핸들 `_curFile`(`_setCurFile`: 열기 창으로 불러온 .ceramic·다른 이름으로 저장한 파일, 새로만들기·DXF·파일 칸 불러오기면 없음)에 창 없이 덮어씀(권한 `requestPermission`),
    없으면 "다른 이름으로 저장"(`saveProjectAs`, `#btn-save-as`, Ctrl+Shift+S = 예전 저장 창 → 고른 파일이 `_curFile`)
- 저장 안 한 변경 알림(2026-11-07 사용자 요청): `_docSig()` = 도형·제품·작업 정보·원판 배치·3D 설정 JSON('_' 속성 뺌, 화면 이동·배율·단가 제외),
  `_markSaved()` = 기준(처음 열 때 load+300ms·새로 만들기·불러오기·DXF 불러오기, 저장·다른 이름으로 저장·다운로드 저장 성공 때 `_savedSig`) → `beforeunload`에서 `_isDirty()`면 브라우저 확인 창(문구는 크롬이 정함, 저장 단추 넣을 수 없음)
- 도형 kind: `rect`(x,y,w,h,rotation,cornerType/cornerSize,corners,groupId/groupRole/applianceType,pieceName,shapeNum,hideDims),
  `line`(x1..y2, DXF 곡선 근사면 arcR/arcMid), `circle`(cx,cy,r,holeType: faucet|outlet|cut), `arc`, `ellipse`,
  `grindregion`(밑면연마, inward, depth), `gosramark`(고스라, outward), `dimline`, `jollymark`,
  `note`(도면 글자: x,y(가운데),text,fs=도면화 px,color — 편집 화면은 fs×0.34px 가운데 맞춤, 도면화는 줄마다 편집 화면에서 보이는 왼쪽 끝(`_noteLineLefts`, _annRef 기준 mm)에서 왼쪽 맞춤(2026-11-20 사용자 요청 "넣은 위치에 고정"), `getBBoxAny`는 편집 화면 글자 상자. 누르기 `_noteHit` = 주석 틀(`_annRun`)에서 `_noteBoxPx` + 8px, hitTestAll pri -3(맨 먼저), 선택 도구 더블클릭 = `_noteEdit` 제자리 입력 칸 `#note-edit`(Enter 적용·Shift+Enter 줄·Esc 취소·blur 적용), 2026-11-23 사용자 요청), `arrow`(화살표: x1..y2=촉, bend 휨, color — 그린 뒤 양 끝 점 끌기/길이 입력으로 크기 수정), `linkmark`(연결 표시: x1..y2 따라 물결 2줄, color; `vein:true` = 결 방향(2026-11-20, 편집 도구 `veinmark`·보조 칸 `#vein-sub`): `_linkWaves`가 큰 물결 한 줄(sin3πt·sinπt, 진폭 `_veinAmp` = 길이 7%, 양 끝 평평)+끝점(x2,y2)에만 화살촉을 돌려줘 선택·끌기·DXF 공통, 방향 바꾸기 `flipVein`(두 끝점 맞바꿈, 속성 칸 ⇄), 글자 `_VEIN_TXT` "결 방향"은 drawLinkMark·DXF text) — 주석이라 조각/가공비/원판 배치에서 제외
- 싱크볼/쿡탑 = `groupRole:'main'` rect (라운드=싱크볼, 직각=쿡탑) + 싱크볼은 둘레 고스라 4개
  - 둘레 고스라 넣기/빼기(2026-11-20 사용자 요청 "인셋형은 고스라 없음"): 싱크볼 도구 보조 칸 `#sinkbowl-sub`(`setSinkGosra`, `_sinkGosra`·localStorage `scd_sink_gosra`) = 새 싱크볼 기본값 + 선택한 싱크볼에 적용,
    속성 칸 `_sinkGosraRow` → `setSinkGosraSel(on)`(`_sinkAddGosra` = groupRole top/bottom/left/right 4개 + `syncGroupShapes`, `_sinkDelGosra`). 고스라 없는 싱크볼은 선택하면 본체 하나
  - 편집 화면 자기 폭·높이 치수(`drawDims`, 2026-11-03 사용자 요청 "겹쳐서 고르기 어렵다"): 화면에서 90×60px 넘으면 안쪽(`inW/inH`: 아래 변·왼쪽 변 14px 안, 보조선 없음),
    작으면 위치 치수(drawNestDims = 상판 변에 가까운 쪽)의 반대쪽 바깥. 사용자가 끌어 옮겼으면(dimUserOffsetW/H) 그대로
    — 묶음이 선택돼 있으면(여러 개 선택 `_onSel` = 도형 끌기 우선) 원래 치수 클릭을 건너뛰지만, 본체의 w/h 글자는 예외로 치수 편집(2026-11-04)
- 왼쪽 도구 묶음(2026-11-07 사용자 확정): 커팅 가공(사각·타공·원형·타원형·직선 커팅) / 객체 삽입(싱크볼·쿡탑·식기세척기·음식물투입구) / 추가 가공(모서리 라운드·밑면연마·졸리컷·고스라) / 편집(트림·분할(`cut`)·치수선·연결 표시·글자 삽입(`note`)·지시선(`arrow`))
  - 도마 `doma` 도구(2026-11-23 사용자 요청, 음식물투입구 아래) = 보조 칸 `#doma-sub` 크기(`setDomaSize`, `_DOMA_SIZES` 200×300·300×400·400×600, `_domaSize`, 넣으면 처음 크기로) → 누른 자리 가운데 R10 rect `groupRole:'main'`·`applianceType:'doma'` + 같은 groupId로 둘레 고스라 4개(`_sinkAddGosra`). 안쪽 전체 = 밑면연마: 편집 화면 `drawShape`·도면화 ③-2·DXF(`SC-GRIND` HATCH, R12는 없음)가 안을 빗금으로, 이름 "도마" + 크기 W×H를 안쪽 가운데에.
    가공비는 도마 금액 하나만 — calcCost가 도마 groupId의 고스라·밑면연마를 건너뜀(2026-11-23 사용자 요청 "도마 개당 금액"). `fullEdge` 밑면연마(syncGroupShapes 변 전체 따라감)는 남아 있지만 도마는 안 씀(재료가 바깥 = 쿡탑·식기세척기와 같은 `_matOut` 목록, 갈색, 이름 "도마")
    → 가공비 `_domaKey(s)` = 가장 가까운 기본 크기의 `doma1~3`(절단 가공 "도마" 줄). 단가 칸은 `_EXTRA_PRICE_ROWS`가 다섯 단가 판에 JS로 끼워 넣음(원가 4·6·8만, 업체·소비자·취급점 5·7·9만), `_FIXED_TIER_KEYS` = 원가 바꿔도 ×1.2·×1.3 안 함
  - 모서리 R 금액(2026-11-23 사용자 요청): 사각 조각(groupId 없음)의 라운드 코너 하나마다 R 구간 `r100`(R50~100)·`r150`·`r200`·`r250`(R250 넘어도 이 단가), R50 미만은 없음 — calcCost `cnt.r*`, 오른쪽 내역은 구간마다 줄 `pl-/ps-r100…r250`(도마도 크기마다 `pl-/ps-doma1…3`, 2026-11-23 사용자 요청 "퉁치지 말고"). 밑면연마 내역: 맨 위 "밑면연마" 줄(`pl-/ps-grind`) = 세 가지 합친 표시만, "└ 100mm 미만"(`pl-/ps-grindmid` = `lenMm.grind`, 깊이 100 미만 전부·50 포함, 보통 단가)·"└ 150×150"·"└ 100mm+". 도마 단가 = 넣을 때 고른 크기 `s.domaKey`(크기 바꿔도 그대로, 없으면 예전처럼 가까운 크기). 선 조각의 호 코너는 안 셈
  - 밑면연마 150×150 원클릭(`grind150mode`, mousedown): 누른 점 = 한 꼭짓점, 네 방향 중 150×150 안 5×5 점이 재료(`_inAnyPiece`, 타공부 제외)에 가장 많이 드는 쪽으로(2026-11-23 사용자 요청 "클릭 점 내부로") — 가로 변이면 가로 띠 + inward = 세로 방향
  - 밑면연마 "100mm+ 모드" 단추는 없앰(2026-11-23) — 150×150 원클릭만, 깊이 100 이상 띠는 calcCost가 계속 grind100 단가로
  - 식기세척기(상부개폐형) `dishwasher` 도구 = 누른 자리 가운데 470×460 `groupRole:'main'`·`applianceType:'dish'` rect(고스라 없음, 쿡탑처럼 재료가 바깥) → 가공비 `cnt.dish` × 쿡탑 단가(`gta('cook')`), 편집 색 보라, 도면화 이름 "식기세척기"
  - 음식물투입구 `foodhole` 도구 = 보조 칸 `#foodhole-sub` 모양(`setFoodShape`, `_foodShape` 'c'|'r', localStorage `scd_food_shape`, 2026-11-21 사용자 요청):
    사각 = 사각 타공 rect(`applianceType:'hole'`) + `food:true` 202×264(`_FOOD_RW/_FOOD_RH`, 가공비 `cnt.food`, 이름 음식물투입구, 갈색) / 원형 = `circle{holeType:'food', r:80}`(Φ160, 고스라 없음) → `cnt.food` × 단가 키 `food`(TIER_KEYS, 기본 원가 20,000 = 콘센트 타공 2배, 업체 ×1.2·소비자 ×1.3, 취급점 20,000)
- 위치(관계) 치수 `drawNestDims`(2026-11-07 사용자 요청): 객체 삽입(싱크볼·쿡탑·식기세척기·음식물투입구)과 타공(수전·콘센트 원, 사각 타공, 타원 타공) = 상판 상자 네 변 모두
  (사각·타원 = 상자 변에서, 원 = 중심에서 `drawCircleGapDim(...,mid)` 글자는 선 가운데). 원형 커팅(holeType cut)·타원형 커팅(hole 아님)은 위치 치수 없음.
  원 타공(수전·콘센트·음식물)은 같은 상판 상자 안 가장 가까운 싱크볼(`_nearSinkBox`)의 가까운 세로·가로 변까지도(2026-11-19 사용자 요청, 숨김 키 `sinkH/sinkV` = drawCircleGapDim 10번째 인자·dimLabels `hk`, 싱크볼 안이면 없음).
  도면화·DXF 이웃 치수 = `_nestNbPairs(조각 holes+cutouts, _nbSkipStd)`(같은 쌍·축 한 번, 같은 줄 같은 종류 원 타공 가로·원 ↔ 가장 가까운 싱크볼은 뺌, 원이 끼면 그 중심선을 따라)
  → 도면화 `_expBestDim`(offsets 0~170, `txtLine:6` = 치수선이 다른 글자 지나면 큰 벌점), DXF `dim()` 가로 아래·세로 오른쪽. `_expBestDim`은 바로 옆(12px) 나란히 겹치는 선도 벌점(2026-11-19).
  표시 조건(2026-11-19 사용자 요청 "상판 고르면 모든 객체 연장선이 나와 이동점 잡기 어렵다"): 그 객체 올림 또는 선택(바깥 상판도 같이 선택이면 안 나옴) — 상판 선택·올림으론 안 나옴.
  끌어 옮기는 중 스냅(`applySnap`을 `_inSnapScope`로)·마그넷(`doMagnet`) 대상 = `_dragSnapScope()` = 선택 상자를 처음 감싸는 가장 작은 사각형 하나 + 선택 (2026-11-19 사용자 요청 "최초 외부 사각에만 스냅"),
  사각형 안이 아니면 감싸는 닫힌 선 조각(`_lineGroupAt`)의 선들, 어디에도 안 든 조각이면 null = 모든 도형(2026-11-20 "조각끼리 꼭짓점 스냅이 안 된다" 수정). 끌기 한 번 동안 `_dssC`에 고정
  이웃 관계 치수 `_nestNeighborDims`(2026-11-19 사용자 요청 "옆 타공 중심까지 거리도", 편집 화면): 타공·객체 삽입(`_isNestItem`)마다 같은 상판 상자 안 이웃 중 왼·오른·위·아래 방향마다
  그쪽에 완전히 있고 옆 범위가 `_NEST_NB_M`(300) 안에서 겹치는 가장 가까운 하나 → 원 = 중심, 나머지 = 상자 변(`_nestRef`) 사이. 원 타공은 싱크볼 치수로 나온 싱크볼 제외.
  숨김 키 nL/nR/nT/nB(`drawGapDim`·`drawCircleGapDim`의 hk, 속성 칸 `_nbToggles`), 누르면 이웃 기준 점 상자 {x,y,w:0,h:0}로 `showGapDimInput`, 글자는 선 반대쪽(아래·오른쪽)
  도면화·DXF 타공도 같게: 가까운 외부 끝변(상판 바깥 변 `pV/pH`, DXF `refs(o)`) + 싱크볼 변(도면화 `_holeRowDims(sinkSegs,true)` 가로 치수 아래쪽, DXF `refs(o,'sink')`) — 같은 줄 타공 사이 간격은 한 번만.
  치수를 누르면 `showGapDimInput`(타원 타공 이동 포함) — "✕ 삭제" 단추(`#dim-hide-btn`) 또는 값을 안 고친 채 Delete = `hideDims[dir]`, 속성 칸 ← → ↑ ↓로 다시 켬. 묶음 선택 중에도 gap 치수는 클릭됨
- 사각 타공(2026-10-29) = 타공 도구의 "사각"(`pendingHoleType='rect'`, W×H 칸 `#hole-rect-w/h` 기본 200×50, `_rectHoleWH`) → 누른 자리 가운데에
  `groupRole:'main'`·`applianceType:'hole'` rect(고스라 없음). 가공비 `cnt.holeo`(콘센트 타공 금액), 편집 색 청록, 도면화 이름 "사각타공", 3D는 그냥 구멍(볼·유리 없음, 도어 나누기에 안 씀)
- 타원 타공(2026-10-30) = 타공 도구 "타원"(`pendingHoleType='ell'`, 같은 W×H 칸) → 누른 자리 가운데 `ellipse{hole:true}`. 가공비 `cnt.holeo`(타원 절단의 둘레 단가 아님), 편집 색 청록, DXF `SC-HOLE`(점선)
- 캡슐 타공(2026-11-20 사용자 요청, 타공 도구의 "타원" 단추를 대신함 — 예전 타원 타공 도형은 그대로 읽고 그림) = "캡슐(콘센트)"(`pendingHoleType='cap'`, 칸 `#hole-cap-d`(Φ 60)·`#hole-cap-l`(중심 거리 71), `_capHoleDL`)
  → 사각 타공 rect + `capsule:true`(cornerType fillet, cornerSize = 짧은 변/2를 `redraw` 처음 `_capSync`가 늘 맞춤). `_capDims(s)`={D,L,hor}, `_capSet(s,D,L)` = 가운데 기준 크기.
  편집 화면 `_drawCapDims`(drawDims 대신: 중심 사이 치수 `capL` + 오른쪽 아래 반원 Φ 지시선 `capD`, 누르면 showDimInput, Tab 전환, ✕ = hideDims.capL/capD), 속성 칸 Φ·중심 거리(`liveCap`).
  도면화 = 자기 치수 대신 중심 사이 치수 + cornerLeaders가 R 대신 Φ, 이름 "캡슐타공" / DXF = 중심 사이 dim + rLeader가 'dia' 지시선(바깥) / `_objSize` "(Φ60 · 71)". 타공 단추 이름: 수전 / 원형(콘센트) / 사각(콘센트) / 캡슐(콘센트)
- 타공을 하나 넣으면 크기 칸(`circle-phi`·`hole-rect-w/h`·`hole-cap-d/l`)은 `_holeInputsReset`으로 HTML 처음 값(35·200×50·60/71)으로 (2026-11-20 사용자 요청)
  — 도구 보조 칸 고르기는 모두 넣은 뒤 처음 상태로 `_toolOptsReset`(2026-11-21 사용자 요청): 타공 종류 수전·크기, 음식물 원형, 싱크볼 고스라 넣기, 졸리컷 뒷면. 이 고르기들은 localStorage에 기억 안 함. 새 고르기 칸을 만들면 여기에 넣기
- 타공은 모두 점선: 편집 화면(`drawShape`의 `_holeDash` — 사각·타원 타공, 원 타공은 예전부터) · 도면화(`_drawCleanExport` ② `HD` — 원 타공·사각 타공·타원 타공) · DXF(`SC-HOLE` 선 종류). 싱크볼·쿡탑은 실선
- 사용자 그룹 `userGroupId`(`groupSelected`, 새 id는 쓰는 중인 것과 안 겹치게): 싱크볼·쿡탑 그룹(groupId)은 그대로 두고 그 전체도 사용자 그룹에 넣음.
  `getGroupShapes`는 사용자 그룹 + 멤버의 groupId 전체 + 그룹 사각 조각 안의 싱크볼·쿡탑(예전 파일) + 그룹 사각 조각 안에 든 다른 도형(다른 사용자 그룹 아닌 것, 2026-11-19) → 그룹째 끌면 같이 이동.
  누르기·올림 선택은 `_selUnit(h)`(`_ugRep` = 자신·같은 groupId 멤버·감싸는 그룹 조각 중 사용자 그룹 → 그룹 전체, 싱크볼 둘레 표시 등은 그것만) — 그룹 안 하나만 선택돼 있어도 누르면 그룹 전체(2026-11-19 사용자 요청).
  그룹 안 객체의 위치 치수 고치기(`showGapDimInput`)는 기준 상자가 그룹 상자 밖이면 그룹 전체를 같은 만큼 `shiftS`, 그룹 안 기준이면 그 객체만.
  싱크볼 크기 맞춤 `syncGroupShapes`는 groupId 멤버만
- 편집 화면: `redraw` → `drawShape`/`drawDims`/`drawNestDims`/`drawShapeNumbers` …
  - 주석 크기 = 도면 크기(2026-10-31 사용자 요청 "오토캐드처럼"): `redraw`가 격자 다음 `_annDraw(_redrawBody)` — 배율을 `_annRef`(뷰 맞춤 `fitView`·처음 화면 배율)로 바꿔 그리고 캔버스를 k=`_annK()`(scale/_annRef, 0.4~5)배.
    → px로 정한 글자·화살촉·치수 간격이 도면과 같이 커지고 작아짐. 편집 ctx의 `lineWidth`·`setLineDash`는 `_lwK`로 나눠 화면 굵기 그대로. 손잡이·회전 손잡이·선택 상자·마그넷·트림 강조는 틀 밖(화면 크기).
    치수만 다른 배율(2026-11-02 사용자 요청 "확대하면 치수가 겹쳐 보인다"): `_dimDraw(fn)`이 치수 틀 kd=`_dimKOf(k)`(확대 k>1이면 √k, 축소는 k)로 바꿔 그림 —
    drawDims·drawDimsLine·drawDimsCircle·drawDimsEllipse·drawDimLine(치수선 도구)·drawNestDims·_drawAngleMarks·autoAdjustDims. 새 치수 그리기도 _dimDraw 안에서.
    `dimLabels` 자리는 치수 틀 좌표(화면 ÷ `_annDimCur`) — `hitDim`·치수 끌기(document mousemove, `_annRun`)·`_dimInputPopup`이 변환. 그리기 미리보기 도형도 `_annDraw`. 도면화(printRender)는 k=1. 휠 = ×1.1 / ÷1.1
  - 크기 손잡이(2026-10-30 개발판에서 만들어 합침): 선택 도형 하나(싱크볼·쿡탑 묶음이면 본체) `_rszTarget` → `drawHandles`가 손잡이(`_rszHandles`, 위치 `_rszHs`) —
    사각형 꼭짓점 4·변 가운데 4(반대쪽 고정, 돌린 사각형은 그 축 `_rszFrame`) / 원 둘레 4(지름) / 타원 두 축 끝 / 선 양 끝 /
    밑면연마·고스라·졸리컷 양 끝(`_isMarkRsz`: groupId 없고 sym:false 아닌 것, 2026-11-23 사용자 요청 — 스냅 잡은 점을 원래 선에 내려 그 선 위로만, 최소 1mm). 누르면 `_rszStart`(saveHistory) → 끌기 `_rszApply`(자기 점엔 스냅 안 함) → 놓으면 `_rszEnd`
    (싱크볼 `syncGroupShapes`, 바뀌었으면 저장 배치 초기화). 끄는 중 숫자+Enter = `_rszTyped`(사각 꼭짓점 "가로,세로"·빈 쪽은 그대로, 변 = 그 치수, 원 = 지름, 타원 = 그 축 길이, 선 = 길이), Esc = 처음 크기, 마우스 옆 `_rszOverlay`
    사각 꼭짓점·타원 축 손잡이(`_rszCorner`, 싱크볼·쿡탑 포함, 타원은 잡은 축 칸부터·돌렸으면 "축1/축2")는 가로·세로 두 칸, 치수 글자 칸도 Tab = w↔h·rx↔ry — Tab(또는 , 스페이스 x)으로 `_rsz.fi` 전환, 겹쳐 보기 "가로 700 × 세로 ▏"(2026-11-03 사용자 요청)
  - 움직임 효과: `_fxScan`(redraw마다 지난번 도형 Set과 비교) → 새 도형 `_fxIn` 0.22초 나타나기, 지운 도형 `_fxOut` 0.18초 사라지기(`_fxDraw`), 대부분 새 객체(불러오기)면 효과 없음.
    되돌리기는 `undo()`가 `_fxUndoPrev`(id → 복사본)를 남겨 id로 비교: 다시 생김 = 나타나기, 없어짐 = 사라지기, 자리·크기·각도(`_FX_KEYS`) 바뀜 = `_fxMorph` 0.24초 미끄러지기. 효과 중 rAF로 다시 그림(선·타원·손잡이 미리보기 같이)
  - 3D 디자인 창을 누르면(capture, 바꾸기 전) `_3dSnapFade` = 3D 화면을 찍어 덮었다가 0.38초 동안 걷어냄(디자인 바뀔 때 스며들듯)
- 선 절단 도구 = 오토캐드 LINE 방식(`lineChain`, `_lineAddTo/_lineMouseUp/_lineKey/_lineOverlay`): 클릭 = 시작점 → 마우스를 움직이면 미리보기 선 + 동적 입력(`_lineDynInput`:
  선 옆 점선 치수의 길이 칸(파랑 선택 = 바로 치면 바뀜, 입력 중엔 친 글자), 시작점 수평 기준 점선 호 + 각도 칸, 커서 옆 "다음 점 지정 또는 길이 입력")
  → 클릭(또는 끌다 놓기, `_lineMouseUp`) = 그 점(직교·스냅 적용)까지 바로 선 / 움직이며 숫자 + Enter(`_lineKey` → `_lineTarget`) = 마우스 방향으로 그 길이
  (누른 채 숫자로 그렸으면 놓을 때 무시: `lineDown.nseg`), Tab = 지금 방향으로 길이·각도 입력란(`#line-pop`, 각도 칸 커서, 0°=오른쪽 반시계). 끝점에서 계속 이어 그림, 끝나도 도구 유지
  `300,-200`(상대, 위가 +)·`500<90`(길이<각도), 빈 Enter/Esc/오른쪽 클릭=끝, C=닫기, U=마지막 선 취소. 기본 직교(Shift=자유). 전역 mouseup의 `finalizeShape`는 line 제외
- 타원 절단 도구(`ellipse`, 2026-10-30 사용자 요청 "캐드 ELLIPSE 그대로", `_ellSt`/`_ellClick`/`_ellKey`/`_ellPreview`): 축 끝점 → 다른 끝점 → 다른 축 거리(첫 축에서 수직 = 반지름) / C = 중심 → 축 끝점 → 거리,
  단계마다 클릭 또는 숫자+Enter(2단계 마우스 방향 길이, 3단계 반지름), 기본 직교(`ortho`, Shift 비스듬히), Esc 취소, 마우스 옆 안내 글자. → `ellipse{cx,cy,rx,ry,rotation}`(가로·세로 축이면 rotation 0, 아니면 −90°~90°)
  - 돌린 타원 공통 도우미 `_ellHalf`(회전 포함 상자 반폭·반높이)·`_ellPts`(둘레 점)·`_ellLocal`(점 → 타원 로컬): getBBox·클릭 판정·조각 안 판정·편집/도면화 그리기(ctx.ellipse 회전 인자)·원판 배치(`_boardPiece` path)·3D·치수 축 방향
  - 가공비 = 원형 절단(`lenMm.circlecut`) 둘레, 원판 배치 칸 = 회전 포함 상자·글자 "타원 장축×단축", 도면화·DXF 치수 = 두 축 길이(축 방향 그대로 바깥)
  - 타원 둘레 가공 표시 `_ellMarkFor(tool,…)`(finalizeShape에서 grind·jollycut·gosra 도구, 두 끝점이 타원 둘레 위면): 둘레 `_ELL_N`(72)등분 점(= `_ellPts`, 3D 옆면 변과 같은 점 → 3D 졸리컷·고스라 면도 맞음)을 잇는 짧은 직선 마크들,
    끈 구간(짧은 쪽) 또는 누르기만 하면 한 바퀴, 한 묶음 = 새 `userGroupId`. 재료 쪽(타원 조각 = 안, 조각 안 타원 = 바깥)으로 grind `inward`+`inwardOverride`·gosra `outward`,
    ★·▲·깊이 글자는 가운데·18칸마다만(`sym:false` = 편집/도면화/DXF에서 기호 안 그림, grind는 hideDims.dist). `_gosraDir`도 타원 조각/타공부를 앎
  - 스냅(`snapPoints`): 타원 두 축 끝점 4개 + 중심(snapCircleCenter), `applySnap`에서 grind·gosra·jollycut 도구는 타원 둘레(360등분 가장 가까운 점)에도 'edge'
- 치수선 도구(`dimline`, `dimLineType` dist|r|phi|ang, `_dimSt`, `_dimClick/_dimPreview`): 길이 = 두 점(클릭 또는 끌기) → 마우스로 위치 → 클릭
  (`_dimBuildLinear`: 두 점 위·아래면 가로, 옆이면 세로, Shift 비스듬히. 저장 x1..y2=기준선, offsetMm(음수=반대쪽), e1/e2=실제 점까지 보조선 연장),
  각도 = 선/사각형 변 두 개 클릭(`_dimSegAt`) → 마우스 쪽 사잇각(`_dimBuildAng`, x1,y1 꼭지점·x2,y2 호 위 점·a0·sweep),
  R/Φ(2026-11-20 사용자 요청) = `_dimRClick`: 곡선 `_dimCurves`(원·트림 호 arc·곡선 근사 선분 arcR) 변 클릭 = 그 방향으로 바로, 중심점 클릭(`_dimSt.rc`, 미리보기 점선) → 변 클릭 = 그 방향
  (변이 아니면 같은 중심 곡선 중 반지름이 가까운 것) → `_dimRMake`(x1,y1 중심·x2,y2 곡선 위 점). mousedown의 예전 원 클릭·`_dimRCircle` 끌기 코드는 이제 안 탐.
  `_dimCurves`에 사각형 라운드 코너(`_expRectGeo`, 돌린 것 포함)·캡슐 반원도. 판정은 스냅 안 한 자리 `_dimRaw`, R·Φ 모드면 `_dimRHover`가 중심마다 + (잡힐 것 주황)·안내 글자
- 코너 R·C 지시선 ✕ 삭제(2026-11-20): 균일 = `hideDims.cornerSize`, 코너별 = `hideDims.r_코너`(dimLabels `field:'cornerR'`+`key`, showDimInput이 값 고치기·삭제) → `_rcHidden(s,ck)`를 편집 화면·도면화 cornerLeaders·DXF rLeader가 봄, 속성 칸 R/R↘ 단추로 다시 켬
- 스냅(2026-10-31 점검) `applySnap` 순서: 오브젝트 점(`snapPoints`) → 선 스냅 `_snapLinesAt`(마우스 가까이 지나는 선분만 `_snapSegs`: 선·사각형 변(회전 포함)·원,
  교차점 'x'(가장 가까운 것, 선-원 포함)·가상 교차점 'v'(`snapVirtInter`)·연장선 'ext'(`snapExtension`, 끝에서 3000 안), 보조선 `_snapGuide` → `drawSnapInd`가 점선) →
  도구별 변 붙이기(밑면연마·고스라 'edge', 타원 둘레·곡선 근사 선분 위도) → **그리드는 맨 나중**(예전엔 그리드가 먼저라 변 붙이기가 막혔음) → 직교. 끄는 중엔 자기 도형 제외(`excl`). "평행"은 아직 없음
  - `_snapCurveBit(s)`(2026-11-03 사용자 요청 "원·타원 뒤 스냅이 너무 많이 잡힌다") = 곡선 근사 선분(arcR/ellArc)·타원 둘레 표시 묶음(sym:false) → 점 스냅(`snapPoints`)·선 스냅(`_snapSegs`, 연장선·가상 교차점)에서 뺌. 점 스냅 허용 = 12px 그대로(예전 13)
  - 마그넷 `doMagnet(arr)`: 여러 개·그룹도 — 전체 상자 + 각 도형 `getEdges`(회전 포함 상자 왼·가운데·오른/위·가운데·아래, 선은 양 끝)를 다른 도형 기준에 맞춰 선택 전체를 `shiftS`(+싱크볼 `syncGroupShapes`),
    거리 = max(마그넷 mm, 10px/scale), 분홍 보조선 `magnetLineX/Y`. 마우스 줄맞춤 하늘색 `drawGuides`도 getEdges·4px
- 코너별 라운드·모따기(`s.corners`) 최대 = `_cornerLim(corners,ck,w,h)`(2026-11-03): 같은 변 이웃 코너가 둥글지 않으면 그 변 전체, 둥글면 절반 —
  `_rcInfo`(도면화·3D·DXF·원판 `_expRectGeo`)·`buildCornerPath`(편집 화면)·코너 R 치수·트림 `_cornerInfo`가 씀. 균일 cornerType은 예전대로 짧은 변 절반
- 판정 공통: `isInsideRect`(회전 포함), `_axisBox`, `_rightAngle`, `findEdgeContext`, `_lineBoundaryGroups`, `_gosraDir`
  - 공통 도우미(새 코드는 이걸 쓰고 같은 계산을 다시 쓰지 않기): `_rectXf/_rectCorners`(회전 rect 꼭짓점), `_isAnnot`(주석 도형 제외),
    `_nearestEdge`(트림·호버 변 찾기), `_isCutRect`(타공부 사각형), `_drawRLeader`(R·C 지시선 글자), `_ymd`(20261021), `_TOOL_SUBS/_TOOL_FOCUS`(도구 보조 칸)
- 미세 이동(2026-11-20 사용자 요청): 선택 끌기 중 Shift = 마우스 움직임 × `_FINE_K`(0.2), 스냅 안 한 마우스 기준·마그넷 없음(`_fineDrag`={a 누른 자리, b 그때 이동점}, `_lastDragPt`),
  Shift를 떼면 dragStart를 옮겨 그 자리에서 이어감. 끄는 동안 `coord-lbl`에 Δx·Δy
- 선택 도구 누르기·커서 공통 판정 `_selPick(ex,ey)`(2026-11-19 사용자 요청 "커서 모양과 달리 끌린다"): 스냅 안 한 실제 마우스 자리로 hits·선 조각 안쪽(`_lineGroupAt`, 필요할 때만)·치수(여러 개 선택 위 건너뛰기 포함) →
  mousedown이 이걸로 고르고, mousemove 커서 `_selCursor` = 회전 손잡이 grab / 치수 화살표·글자 / 도형·선 조각 안 move / 빈 곳 crosshair. 선 잡는 범위 `hitTestAll` tol 8px(예전 6)
- 선택: `hitTestAll`(사각형 안쪽(pri 1)끼리는 넓이 작은 것 먼저 — 안의 싱크볼·타공이 바깥 상판보다, 2026-11-20 사용자 요청; 같은 자리 다시 누르면 `_cycleIdx`로 다음), 조각 변의 밑면연마 -1·고스라/졸리컷 선 -0.5, ▲·★ 기호 위 = -2 맨 먼저, 싱크볼 둘레 표시는 제외), `_markAreaHit`(밑면연마 빗금 띠·고스라 ▲·졸리컷 ★ 위도 선택),
  `_markSym(s,k)` = 편집 화면 ▲(변 가운데 바깥)·★(변 가운데에서 안쪽으로 반지름만큼, 2026-11-03) 자리 → 그리기·`_markSymHit`(최소 9px) 공통, 올림·선택이면 둘레 빛 + 1.5배(선택 주황),
  마우스 올림 강조 `hoverShape` = `hitTestAll`의 첫 도형(클릭 결과와 같음): 고스라 진한 빨강 굵은 실선·큰 ▲, 밑면연마 빗금 칸 진하게+테두리, 졸리컷 진한 파랑, 도형 파란 테두리·채움
  (아무것도 선택 안 했을 때 올리기만으로 잡힌 선택(`_hoverSelected`)보다 강조색이 먼저)
- 곡선 트림(2026-11-03 사용자 요청): `doTrim`이 `_nearestCurve`(원형 절단 `holeType:'cut'`·호·타원, 타공 원 제외)가 변보다 가까우면 `_trimCurve` —
  원·호는 각도로(교점 `_segCirc` 선-원·`_circCirc` 원-원, 호 범위 `_arcNorm/_angIn`): 원 = 클릭 구간 빼고 호 하나(교점 1개면 못 자름, 0개면 지움), 호 = 줄이거나 둘로;
  타원 = `_ELL_N` 꺾은선 위치로 → 남는 부분은 line들(`ellArc:'타원 장축×단축'`, 가운데 하나 `ellMid` — arcR처럼 길이·각도 치수 없이 그 글자만: drawDimsLine·_lineAngleMarks·_lineDimPlan·도면화·DXF, 선 트림하면 복사). 선·사각형 변을 자를 때 교점은 `_trimHitsSeg`(선·사각형 변·원·호·타원 모두). 트림 호버는 곡선 전체 빛(`trimHoverEdge.curve`)
- 자르기 도구(`cut`, 2026-11-03 사용자 요청 "1000×500 → 400×500 / 600×500", 트림 아래 단추): `_cutSt` 단계 — 변 클릭(`_cutFind`: rect·선 조각 고리 `_cutLineLoop`·원·타원·열린 선, 사각형은 진짜 꼭짓점 `st.rc`에서 변 따라 잼)
  → 1단계 P = 둘레 따라 마우스(`_cutMove`/`_cutSetP`, 정수 mm)·숫자+Enter = 거리·끌다 놓기 → 2단계 가르는 선 `_cutChord`(기본 = 변에 수직, 원·타원은 진짜 법선, Shift = 마우스 방향, 숫자+Enter = 지나온 변과의 각도) → 맞은편 변 Q
  → `_cutDo`: 회전 없는 사각형 축 방향 = `_cutRectAxis`(사각형 둘, 코너는 제자리 쪽), 그 밖 = `_cutSplit` 두 고리 → `_cutLines`(선 조각, 곡선 근사 = arcR/ellArc 가운데만 글자). `_cutMarksAt`가 P·Q에서 고스라·졸리컷·밑면연마를 둘로.
  자른 뒤(2026-11-03 사용자 요청): 가르는 선 법선 중 오른쪽(세로가 아니면 아래) 조각 + 그 안·둘레에 딸린 것(`rides`: 싱크볼 그룹·타공·가공 표시·글자)을 `_CUT_GAP`(100) 옮기고 `_fxMorph`(항목 `d` = `_CUT_ANIM` 420ms)로 미끄러짐, `_fxPrev`를 바로 맞춰 나타나기/사라지기 효과는 없음.
  원·라운드 코너 선분은 `arcS`(원 중심이 선 법선(-dy,dx) 쪽 +1/-1) → `_arcCtrOf`로 중심 복원 → `_findCornerAttach`가 곡선으로 인식(가공 표시 곡선 유지), `_cutMarksAt`은 호 표시를 호 위에서 나눔. 원·타원 P·Q는 `_cutOnCurve`(진짜 둘레), 사분점·축 끝에 붙음.
  "못 자름" 방지: 재료 쪽 판정은 지나온 변 위(P − u·0.5)에서(ㄱ자 안쪽 꼭짓점), 원·타원은 진짜 법선(폴리곤 판정 안 씀)·자기 변 제외·최소 3mm, 거꾸로 왔으면 `_cutAt(…,back)` = 지나온 변,
  사각형 꼭짓점 시작(`rc`)은 거리를 [시작 코너 R, 변 − 끝 코너 R](최소 1)로 맞추고 기준 변 = 나란한 곧은 변, 가르는 선 양옆이 모두 재료여야(모서리를 따라가는 선 = 못 자름, `st.why`)
  원 `_findCornerAttach` matOutward = 원형 절단이 다른 조각 안(`_inAnyPiece`)일 때만(단독 원 조각은 안쪽 재료). 원형 절단이 조각 밖이면 `drawNestDims` 관계 치수 없음.
  도면화 밑면연마: 호에 붙은 것 = `_expHatchArc`(부채꼴 띠, 재료 쪽 `_matAt`), 곧은 띠는 `_gBands`로 모아 끝이 맞닿은 띠(같은 깊이·같은 쪽)는 `_expHatchBand`의 j1/j2로 꺾어 이음(타원 둘레)
  선 `lp`(조각 표지) = 맞댄 두 선 조각이 끝점으로 안 묶이게 — `_cutLpOk`를 `_collectBoardItems`(겹친 선 하나만·이어짐)·`_lineBoundaryGroups`가 씀. 둘째 조각 가르는 선 `cutTwin` = 편집 화면 길이 치수 하나만. 미리보기·안내 `_cutPreview`
- 결합 도구(`join`, 분할 아래, 2026-11-23 사용자 요청): `_joinSt` 단계 — 기준 조각 클릭(`_joinFind` = `_cutFind` 변 근처 또는 안쪽 가장 작은 사각형·원·타원·닫힌 선 조각) → 붙일 조각 클릭
  (`st.mv` = 조각 + `_joinRiders`(안에 든 것·둘레 가공 표시·같은 groupId, 기준 조각 제외), `st.h0` = 옮기기 전 기록) → 마우스 따라 실제로 옮김(`_joinSetD`), 붙일 조각 점(`_joinPts`: 사각형 꼭짓점·변 가운데·라운드 끝, 선 조각 꺾이는 점, 원·타원 사분점·중심)이
  기준 조각 점 14px 안이면 맞춤(Alt = 안 함) → 클릭 = 놓기(`_hist`에 h0 한 번). Esc·오른쪽 클릭 `_joinCancel` = `_joinRestore`(mv0으로) 한 단계 뒤로. 미리보기 `_joinPreview`는 redraw 끝에서.
  놓을 때 `_joinMerge(st)`(2026-11-23 사용자 요청 "붙는 부위는 커팅하면 안 되니 그 선이 없게"): 두 둘레를 반시계로 → 서로의 꼭짓점에서 변 나눔 → 반대 방향으로 겹친 구간(맞닿은 변)을 둘 다 뺌 → 남은 변을 한 고리로(넓이 = 두 조각 합일 때만, 겹침·구멍·한 점만 닿음이면 자리만)
  → 같은 직선 곧은 변 이음 → `_cutLines`로 선 조각 하나(label = 기준 조각 것), 맞닿은 구간 위 가공 표시는 `_cutMarksAt`로 나눈 뒤 지움
- 트림 `doTrim`: rect는 `_trimRectGeo`(90° 단위 회전 = 보이는 대로 회전 없는 rect·코너 키 돌림, 그 밖 각도 = 꼭짓점 `_pts`) +
  `_trimRectEdges`(위→오른쪽→아래→왼쪽, 클릭 판정·교점·분해가 같은 방향)로. 잘린 구간에 겹친 같은 직선 위 선은 `_trimOverlaps`로 같이 지움
- 조각/배치: `_collectBoardItems` → `_packBoardItems` / `_restoreSavedBoards`, `showBoardLayout`, `renderBoardLayout`
  - 트림으로 생긴 호(`arc`)도 선 그룹에 들어감(2026-11-07 사용자 요청): `_arcSegs(a)` = 대리 선분(5° 간격, 짧으면 4mm 이상으로 줄임, `arcR`·가운데 `arcMid`, 도형 목록엔 없음, WeakMap 캐시로 같은 객체),
    그룹은 진짜 선을 앞에(조각 key = lines[0]). 대리 선분 → 원래 호는 `_realOf(l)` — 제품 지정·`_lineGroupAt`(끌기)·3D 구분·조각 순서·`_shapePieceMap`이 씀
  - 조각 = 다른 사각형·닫힌 선 조각 안에 들지 않은 rect/원 + 이어진 선 그룹. 선이 사각형 안인지는 `_lineInRect`(사각형 변 위에 겹친 선은 안이 아님 — 미드웨이를 상판 변에 붙여 그려도 선 조각 유지), 같은 자리 두 번 그린 선은 하나만. 돌린 rect는 회전 포함 상자 크기(`getBBox`)로, 그리기(`_expRectPathLocal`)도 회전 포함
  - 객체 이름(2026-11-07 사용자 요청): `_boardPiece`가 타공부·타공 가운데에 `_objName(q)`(싱크볼·쿡탑·식기세척기·사각타공·타원타공·수전·콘센트·음식물, 원형 절단은 없음)을 칸에 맞게(9px 미만이면 생략),
    조각 이름·크기 글자가 객체 상자와 겹치면 조각 안 빈 곳(5% 격자, 가운데에 가까운 곳, 선 조각은 `_Minv`로 글자 상자가 조각 안인지 확인)으로 옮김.
    빈 곳이 없어 글자가 구멍 위에 남으면 객체 이름을 그 글자 상자(`_LB`) 위/아래(안 되면 옆)로 비켜 씀, 구멍 안에 자리가 없으면 이름 생략 — 이름은 글자 자리를 정한 뒤 그림.
    돌려 놓은 조각(`p.rotated`)은 크기 글자를 `_swapWH`로 원판에 보이는 가로×세로(↻ 그대로), 객체 크기 `_objSize(q,turn)`도 객체 회전+배치 회전이 90° 홀수 배면(`_oddTurn`) 바꿔 씀(2026-11-19 사용자 요청)
    이름 아래 둘째 줄 `_objSize(q)` = "(가로×세로 R24)"(코너 `_rcInfo` R·C, 코너마다 다르면 R20/C10)·타원 "(장축×단축)"·원 "(Φ지름)"(글자 0.78배), 두 줄이 9px 미만이면 이름만
  - 원판보다 커서 못 놓은 조각(2026-11-02): `_packBoardItems`가 `unplaced`([{item,prod,bw,bh,ew,eh}])로 돌려줌 → `showBoardLayout`이 머리줄 아래 빨간 상자 `#board-modal-warn`에
    `_unfitReason`(조각 번호·이름·크기·제품 + 긴 변/짧은 변이 원판 유효 길이/폭(여백 10씩 뺌)보다 큰지) — 저장 배치 복원 때는 없음(못 놓은 조각이 있으면 복원 안 됨)
  - 미배치 칸(2026-11-02 사용자 요청): 원판 배치 창 오른쪽 `_bsParkW` 폭(창에서만, 도면화 그림엔 없음, `_bs.parkX` = 칸 시작 px, 다음 쪽 화살표도 그 왼쪽).
    조각을 끌어 칸 위에서 놓으면(`_bs.overPark`) `_bs.parked`로, 칸 조각을 누르면 `_bs.parkDrag`(원판 배율로 커서에, 놓을 수 없는 원판이면 빨간 테두리) → 원판 위 놓기 `_bsPlaceParked`(같은 제품만·`_bsFitDims`),
    칸에서 오른쪽 클릭 = 90°. 칸 조각마다 위에 제품명(`_itemProd`, 제품 색 ■, 칸 폭에 맞게 …로 줄임). 겹침 정리 `_bsResolve`(밀어내고 그래도 겹치면 놓은 조각을 가장 가까운 빈 자리로), 빈 장 정리 `_bsCleanBoards`(빈 장도 제품 이름 유지).
    남긴 채 닫으면 confirm → `_bsAutoPlaceParked`(같은 제품 원판 빈 자리 10mm 훑기, 없으면 그 제품 새 장)
  - 원판 장수(2026-11-03 사용자 요청 — 머리줄 단추는 보기 싫다고 해서 오른쪽 클릭 메뉴로): 원판 빈 곳 오른쪽 클릭(oncontextmenu, 조각 위는 돌리기) → `_bsCtxShow(bi)` 메뉴 `#board-ctx`
    → `_bsAddBoard(bi)` = 그 장 바로 뒤에 같은 제품 빈 장 `keep`(그룹 count·뒤 그룹 startBi `_bsShiftGroups`), `_bsDelBoard(bi)` = 그 장 빼기(조각은 `_bs.parked`로, 제품마다 최소 1장). `keep` 장은 `_bsCleanBoards`·movePieceTo가 안 지우고,
    저장 배치 `boardKeep`로 복원, `_updateBoardQty`가 수량에 셈(빈 장도)
  - 선 조각 실제 모양 겹침(2026-11-20 사용자 요청 "ㄱ자 따낸 자리에 넣기"): `_bpPoly(p)` = 선 조각 외곽(`_expChain`, `_boardPiece` M과 같은 변환, 원판 유효 영역 mm), 사각형·원은 null →
    `_bsOv(a,b,g)`(상자 → 다각형 안 점·변 거리 < 간격) — `_bsResolve`·돌리기 충돌 해소·`_bsAutoPlaceParked`, `_bsHitTest`도 다각형 안만, 끌기 마그넷에 꼭짓점 후보. 자동 배치(`_packBoardItems`)는 아직 상자 기준
  - 360° 돌리기(2026-11-20 사용자 요청): `p.flip` = 180° 더(칸 안에서 a→FW−a, b→FH−b) — `_boardPiece` M/_Minv·`_3dWorldToBoard`·`_bpPoly`가 적용, 저장 배치 `flip`.
    오른쪽 클릭 `_bsTurn(p,EW,EH)` = 0→90→180→270(rotated/flip), 안 들어가는 방향 건너뜀, 가운데 기준. 글자는 늘 ↻0°/↻90°/↻180°/↻270°(2026-11-23 사용자 요청).
    대칭 조각도 네 방향 모두(2026-11-23 "모든 각도로 안 돈다" — 예전 `_bsSym` 0↔90만·복원 때 flip 버림은 없앰, `_bsSym` 함수는 남아 있지만 안 씀)
  - 여러 조각 같이 옮기기(2026-11-23 사용자 요청): Ctrl+클릭 = `_bs.multi`에 넣고 빼기(파란 점선, 먼저 눌러 둔 pickedPiece도 같이) → 그중 하나 끌기 = `_bs.gdrag` →
    `_bsGroupMove`(모두 같은 mm, 각자 자기 원판 안으로 제한, 누른 조각만 다른 조각·끝에 10mm 붙임) → `_bsGroupDrop`(고른 것 아닌 조각만 비킴, 그래도 겹치면 처음 자리로). 장 사이 이동·미배치 칸은 하나씩만. 빈 곳 클릭 = 풀기, 빈 곳 끌기 = 범위 고르기 `_bs.rband`(걸친 조각, Ctrl = 더하기)
  - 원판 배치 창 휠 줌(2026-11-23): `_bs.zoom`(0.5~8, 마우스 자리 고정 = 그린 뒤 `_bs.panX/panY` 보정)·가운데 버튼 끌기 `_bs.panDrag`·빈 곳 더블클릭 = 원래대로, 2장 보기 배치 계산에서 sc×zoom (targetCanvas = 도면화는 안 씀)
  - 원판 배치 가공 표시 `_bpMarks`(2026-11-23 사용자 요청): `_boardPiece`가 조각(pc)에 딸린 밑면연마(재료 쪽 띠 빗금)·고스라 ▲(`_gosraSym` = 도면과 같은 자리·방향, 꼭지점이 변 위; ▲는 조각 바깥이라 옆 조각에 가려지므로 `_bpDefer`에 모았다가 장의 모든 조각 뒤 `_bpFlush`로 흰 테두리와 함께)·졸리컷 선+★(앞면 ☆)를 M으로 그리고 `p._mk`(px, 재료 쪽 법선)에 남김 →
    장마다 `_bsMarkPairs`(나란·마주 봄·간격 ≤ gap+15mm·겹침 4px 넘음) = 옆 조각과 맞붙은 가공 변을 빨간 띠 + "졸리컷 ↔ 졸리컷"(둘 다 졸리컷이면 진한 빨강).
    옮기기·지우기(2026-11-23 사용자 요청): `_pairOv[키]`(키 = 두 조각 id 정렬 + 변 방향, 파일 `boardPairOv`, 새로 만들기·불러오기에서 바꿈) = {dx,dy 글자 자리 mm(띠 가운데 기준, 멀면 점선), hide}.
    창에서만 `_bs.pairHits`(글자 상자·✕) → mousedown `_bsPairAt` = 끌기 `_bs.pairDrag`/고르기 `_bs.pairSel`(파란 테두리 + ✕), ✕·Delete = `_bsPairHide`, 더블클릭 = 자리 처음대로, 빈 곳 오른쪽 메뉴 `_bsPairShowAll`. 창에서는 빈 자리가 없어도 글자를 가운데에 그림(도면화는 예전처럼 생략)
    한쪽만 가공 변이어도(옆 조각 외곽 변 `p._ed` = `_boardPiece`가 남김, 선 조각은 `_bpPoly`, 원·타원 없음) "고스라 ↔ 가공 없음"(`_MK_NAME.none`) — 마주 보는 가공 변이 있으면 그쪽만. 글자는 이음선 따라 0.5→0.35→0.65… 자리 중 `p._lbox`(조각 이름·크기 글자, `_boardPiece`가 남김)·★▲·다른 띠 글자와 안 겹치는 곳, 없으면 띠만. 도면화 원판 쪽에도 같이 나옴
  - 원판 배치 창: 오른쪽 클릭 = 90° 돌리기(`p.rotated`), Shift+오른쪽 클릭 = 선 조각만 각도 입력(그린 방향 0°, 반시계 +) → `item.rot`,
    저장 배치에 `rot` 기록(`_rotBox`로 상자 다시 계산해 복원)
  - 조각이 작아 안에 크기 글자가 안 들어가면 빈 곳에 글자 + 조각을 가리키는 화살표(`_boardPiece`, `tex.board`/`tex._used`):
    원판 안을 훑어 다른 조각·다른 바깥 글자와 안 겹치고 화살표가 다른 조각을 지나지 않는 자리, 없으면 캔버스 안(잘리지 않게).
    번호 칸도 안 들어가는 조각은 바깥 글자 앞에 번호 칸(`_pn`)을 붙임
  - 선 조각이 그대로 원판에 안 들어가면 변 하나를 가로로 눕힌 각도 중 들어가는(면적 최소) 것으로 돌림(`item.rot/rx0/ry0`, `_boardPiece`의 `M`이 적용)
  - 유광 원판 표시 `_boardSheen`(배치 창·도면화 원판 배치 쪽, 조각까지 그린 뒤): `_prodGloss(장 제품)`>0이면 비스듬한 흰 반사 띠 2줄 + 오른쪽 위 "✦ 유광"/"✧ 반광" 표
  - 원판 배치 창(`renderBoardLayout`)은 제품 수와 상관없이 한 쪽에 2장씩(`goBoardPage` — 배치 그림(`#board-canvas-wrap`) 안쪽 좌우 가운데 큰 화살표 `.board-side-btn` #board-prev-btn/#board-next-btn, ← → 키, 머리줄엔 쪽 번호만). 쪽이 2개 이상이면 원판을 좌우 `_BS_NAVW`(72px) 안쪽에 그려 화살표가 안 가림(2026-11-20 사용자 요청 "캡처 때 걸림"), 창 폭 94vw·최대 1260px. 제품별 행 배치는 그림으로 내보낼 때(targetCanvas)만
- 도면화 버튼 = `drawingMenu`(방식 고르기, localStorage `scd_drw_mode`, 예전 값 'one'은 'area'로):
  `exportDrawingA4('area')`(2026-10-28 사용자 확정) = 1쪽 전체 도면 **모양만**(`_expShapeOnly` → `_drawCleanExport`가 밑면연마·고스라·치수·사용자 치수선·졸리컷·각도·R/Φ·범례를 건너뜀, 외곽·싱크볼/쿡탑·타공·이름·번호·도면 글자만)
  + 구역별 상세 `_areaPages(items)`: 같은 제품이고 상자 사이 `_AREA_TOUCH`(300mm) 이하인 조각끼리 union-find → 제품 순·위→아래·왼→오른쪽, 같은 제품 다음 구역과 합쳐도 배율이 25% 넘게 안 줄면 한 쪽에(작은 판 쪽이 따로 안 생기게).
  다른 제품은 항상 다른 쪽. 이 방식은 번호 보기와 상관없이 조각 번호를 넣음(`showShapeNumbers` 잠시 켬).
  `exportDrawingA4('detail')` = 아래 예전 방식(1쪽 전체 도면에 치수 포함 + 원판별 상세). `_renderDrawingImage` 위 여백 padT = 왼쪽 위 글자 높이(업체 39 + 제품마다 32 + 쪽 설명 37) + 125 이상
- 도면화(PDF): `exportDrawingA4` → `_drawCleanExport`(도면 쪽, `_exp*` 함수들) + `_renderCleanBoards`(원판 배치 쪽, 한 쪽에 최대 2장 `_BPP`, `bi0`로 "원판 N" 번호 유지)
  + 맨 끝 "사용 제품" 쪽 = 제품마다 한 쪽씩 원판 사진(`window._MALL_IMG[id]`, 불러오는 중이면 300ms마다 다시 넣음)·제품명·영문명·사이즈·장수 (공장 확인용)
  - 상세 쪽 조각 손으로 옮기기(2026-11-24 사용자 요청): `_compactPageShapes`가 자동 자리에 `_drwOv['방식:조각키'(_drwPieceKey)]={dx,dy}`(mm, 파일 `drawingOv`, 새로 만들기·불러오기에서 바꿈)를 더하고 `_drwMeta`에 조각 상자를 남김 →
    `_drwRenderPage`(쪽 하나, boxes = 그림 px) · `_drwWithNums`(조각 번호 고정) · `_renderDrawingImage`가 sc/ox/oy/W/H도 돌려줌. 내보낼 때 `_drw`={mode,pmap,items,pages[{pd,sc,boxes,W,H}]}.
    인쇄 창에 `_drwPopupScript`(toString으로 넣음, window.opener 사용): 조각 2개 이상인 쪽 그림 위 올림 = `.drw-hl` 상자, 끌어 놓기 = `opener._drwMove(pi,key,dx,dy)`(그림 px) → 그 쪽만 다시 그려 src 바꿈, `.drw-reset` = `_drwReset(pi)`. 인쇄 때 숨김
  - 도면화 창 치수 지우기(2026-11-24 사용자 요청): `_drwHide[키]`(파일 `drawingHide`) — `_expDim`·`_expLeader`가 `_drwDimKey`(가장 가까운 조각 `_drwMeta` 상자 기준 상대 mm + 잰 점 + 글자, 조각 없으면 'w' 도면 mm)로 숨김이면 안 그리고 `_drwSkip`에,
    그리면 `_drwHits`(글자 상자 px)에 남김(_drwRenderPage 동안만). 창: 글자 올림 = 빨간 `.drw-hl.del`, 누르면 `opener._drwHideDim(pi,key)`, `.drw-bar` "↺ 지운 치수 N개" = `_drwShowDims(pi)`. 모든 쪽에서 됨(조각 옮기기는 조각 2개 이상 쪽만). 편집 화면 hideDims와는 따로
  - 치수 간단히 `_drwSimple`(2026-11-24 사용자 확정 "사람이 보는 도면", 도면화 메뉴 체크·localStorage `scd_drw_simple`, 기본 켬): `_drawCleanExport`에서
    타공 줄 = 300mm 안끼리만, `_holeRowDims`는 상판 바깥 변 + 싱크볼 변을 합쳐 한 번(가로 1·세로 1), `_nestNbPairs` 이웃 치수 없음,
    객체 자기 W/H·캡슐 중심 거리·객체 R 지시선 없음 → ③-2가 이름 아래 `_objSize` 글자. 끄면 예전 그대로(자세히). 조각 치수·타공 Φ 지시선은 그대로
    체인 치수(2026-11-24 사용자 예시 "330/540/330 위에 1,200"): 축에 맞춘 사각 조각(`p._chain`)은 ④에서 dimItems에 `chain:true` 항목을 더함 —
    객체 가장자리 = 그 조각 전체 치수와 같은 변(`objChains`: 같은 시작·끝끼리 한 줄, 나란히 안 겹치면 한 줄로, 변에 가까운 묶음이 안쪽), 타공 중심 = 반대 변(막혔으면 같은 변)·가운데 기준 가까운 끝변부터.
    `_expDimRows`는 같은 변이면 chain 먼저 놓아 안쪽 줄, 전체 치수는 바깥 줄(chain끼리는 공통 치수 묶기 안 함). ⑤는 `p._chain`이면 객체·타공 위치 치수 건너뜀. `_renderDrawingImage` 여백도 간단히면 더 큼
  - 1쪽은 항상 **전체 도면**(모든 도형 원래 자리). 원판 2장 이상이면 2쪽부터 **원판마다 상세 한 쪽**("상세 · 원판 N"): `_drawingBoards`(저장 배치/자동 배치) → `_shapePieceMap`(도형 → 속한 조각: 조각 안·변 위 → 가장 작은 조각,
    밖이면 가장 가까운 조각, 그룹은 main 자리) → 쪽마다 `shapes`를 그 장 조각 것만으로 잠시 바꿔 `_renderDrawingImage`.
    이때 `_compactPageShapes`가 조각(+딸린 도형)을 옮긴 복사본으로 바꿈 — **원래 배치 유지**(2026-10-28 사용자 확정 "설치 위치를 알 수 있게 배치해 놓은 것"):
    가로·세로 축마다 조각 구간을 합쳐 조각이 없는 빈 띠만 150px 상당 mm로 줄임(더 좁은 틈·순서·줄 맞춤은 그대로, 도면 영역 `_DRW_AW×_DRW_AH` 배율로 4번 다시 계산). 줄 맞춰 새로 모으지 않음. 배치 안 된 조각은 따로 한 쪽.
    조각 번호는 `_autoPieceNums`를 `shapeNum`에 잠시 고정해 전체 기준 유지. 도면 쪽은 **항상 가로 A4**(`isPort=false`)
  - (편집 화면) 밑면연마 깊이 글자 `_drawGrindDepthLabel(x,y,depth,band,s)` — 깊이 50(`_GRIND_MM`)이면 안 그림(2026-11-19 사용자 요청) — s를 주면 dimLabels `field:'depth'`(주석 틀 → 치수 틀 좌표) → `showDimInput`이 깊이 고치기·✕ 삭제(`hideDims.dist`, 2026-11-19 사용자 요청): band(띠 상자 px)를 주면 가로 띠 = 왼쪽 끝 바깥, 세로 띠 = 위쪽 끝 위(2026-11-03 사용자 요청), 짧은 띠(길이 ≤ 깊이×1.5, 150×150 원클릭) = `{pt,out}`으로 변 가운데에서 상판 바깥. 사선·라운드 띠는 가운데
  - 밑면연마 띠는 50mm, 단 깊이가 더 큰 것(변의 300 띠, 150×150 원클릭)은 그 깊이로 · 방향 = 선 양쪽 중 재료(조각, 타공부 제외)가 있는 쪽,
    양쪽 다 재료면 저장된 `inward`(가로선 +y, 세로선 +x). 돌린 조각은 `inward`가 로컬 기준이라 그대로 쓰면 뒤집힘(2026-10-28 수정)
  - 끌어 옮기는 치수 글자 공통: `dimLabels` 항목에 `start()/drag(ex,ey,dx,dy,st)` (선택·선 절단 도구 mousedown → `dimDragInfo`, document mousemove가 호출).
    지시선 글자 `s.lblOff[key]=[dx,dy]px`(`_lblOff/_lblDrag`, key: rc·r_코너·phi), 선 사이 각도 호 반지름 `line.angR{a|b}`(px),
    치수선 도구: 길이=offsetMm, 각도=x2,y2(반지름), R/Φ=끝점 회전. 모두 편집 화면 전용(도면화는 자동 자리)
  - 편집 화면 선 길이 치수(`drawDimsLine`): ✕ 삭제 = `hideDims.dist`면 안 그림(2026-11-24 수정, 도면화는 그대로). 끌어서 옮김: `s.dimOffPx`(px, 바깥쪽 +, 자동 자리 8px 안이면 지움 → 자동). 도면화는 자동 자리 그대로
  - 도면화 조각 치수(사각 폭·높이, 선 조각의 가로·세로 선)는 `_expDimRows`(2026-10-27 사용자 확정 "공통 치수 빼고 치수 줄 쭉 맞추기"):
    같은 방향·같은 값·범위 50% 이상 겹침·조각 사이 800mm 이하인 것끼리 묶음(union-find, 이어진 조각 줄 전체) → 하나만.
    쪽(b→r→t→l)마다 바깥 변부터, 기존 줄 중 가장 가까운 줄에 붙임(보조선·치수선이 조각 안을 안 지나고 1500mm 이내, 같은 줄 범위 안 겹침), 없으면 자기 변 옆 새 줄(가까운 줄과 58px 간격).
    `_expDim(...,fixed)` = 치수선은 그 줄 그대로(글자만 자리 고름). 비스듬한 선·돌린 사각형·원은 예전처럼 그 자리
  - (편집 화면·DXF) 선 조각 가로/세로 선 치수는 `_lineDimPlan`으로 조각 상자 바깥 치수 줄(위·아래·왼·오)에 맞춤, 같은 쪽 범위가 겹치면 짧은 것부터 안쪽 줄
  - `_expDim`: 30px 미만 짧은 치수는 화살표를 바깥에서 안쪽으로, 글자는 화살표 너머
  - 범례는 가공이 없어도 항상: 실선 = 닫힘면, 주황 빗금 = 밑면연마(50mm), 검정 ▲ = 고스라, 빨간 ★ = 졸리컷
  - 겹침 방지: `_pdr`(글자 상자), `_pseg`(그린 선), `_pcut`(타공부 안쪽) 등록 후 `_expDim`/`_expBestDim`/`_expLeader`가 빈 자리 선택
- 3D 보기(`show3D`/`close3D`/`save3DImage`, WebGL 직접 구현 — 외부 라이브러리 없음, 닫기는 ✕ 버튼만 — Esc는 `onKey`가 삼킴(2026-10-28 사용자 요청)): `_3dBuildScene`이 `_expCollect` 조각마다
  외곽·구멍 루프(`_3dLoops`: rect=`_expRectPath`, 선 조각=`_expChain`, 싱크볼/쿡탑·타공=구멍), 두께(`_3dThick`, 제품 사이즈 "12T", 없으면 12),
  윗면 텍스처 = 조각 모양으로 오린 원판 사진(`_drawingBoards` 배치 자리 → `_3dWorldToBoard`(= `_boardPiece`의 M) → 아핀 `_afMul/_afInv`로 `_drawSlab` 원판 캔버스를 옮겨 그림, 사진 없으면 돌 색).
  `_3dSetupGL`: 윗/밑면 = 조각 상자 사각형 + 텍스처(투명 버림, 삼각분할 없음), 옆면 = 루프 따라 세운 사각형(법선은 재료 바깥), 윗면 외곽선 = 이음선, 바닥판.
  하부장(기본 켬, 머리줄 "하부장" 체크 `_3d.furn` — 꺼도 상판은 900·세라믹 판은 그대로, 가구만 안 그림): 상판 윗면 900(`_3D_H`), 몸통 = 외곽을 20 들인 다각형(`_3dInset`) 벽, 걸레받이 100(+50 들임),
  민자 도어 = 앞면 변(`_3dFrontEdges`: 밑면연마·고스라 붙은 변, 없으면 도면 아래쪽을 보는 가장 긴 변)에 + 틈 선, 폭 300 미만 조각은 장 없음.
  (2026-11-07 사용자 요청) 표시 붙은 변이라도 800 미만이고 이웃(50 미만 코너 변 건너뜀)에 더 긴 앞면 변이 있으면 측면이라 도어 없음.
  손으로: 상판 도형 `front3d={n:외곽 변 수,e:[변 번호]}`(`_3dFront`, n이 다르면 자동) — 3D에서 상판 고르면(`_3d.sel`, 하부장 켬·오브제 아님) `_3dLabels`가 300 이상 변마다 "🚪 도어"/"+ 도어" 표(`data-fe`) → mousedown `_3dToggleFront`(saveHistory → 되돌리기), tops 항목 `front`.
  모서리 겹침 없음(2026-11-07 "도어는 한쪽에서만"): 이웃 앞면 변이 더 길면(같으면 앞 번호) 짧은 변은 그쪽 끝을 그 변 칸 깊이만큼 비움(`cornerCut`, 직각 근처만) +
  칸 후보 `uCand`를 긴 변부터·앞 줄 먼저 놓고 이미 놓은 칸과 바닥 자리(`uFoot`, 5mm 들임, SAT `uSep`)가 겹치면 버림 → `oneUnit`.
  칸 도어 방향 `_3dStyle.units[칸].r`(0~3, `_3dUnitSet`이 0이면 지움): `oneUnit`이 같은 바닥 자리에서 앞 선·법선을 다른 면으로 바꿔 그림, 종류 막대 "↻ 도어 방향"(`data-ua="rot"`, 하부장 칸, fOp units).
  고른 칸(`selUnits`)의 도어 면 = `_3dLabels`가 unitInfo `c[0]`→`c[3]`(앞 선) × y0~y1 면을 SVG 금색 반투명 + "🚪 도어" 표로(가려져도 보임)
  나누기 `_3dDoorSplit(L,apps)`: 싱크볼·쿡탑 구멍(가장 가까운 앞면 변 하나에, `appAt`) 아래 = 폭+60을 100 단위 올림·가운데(800 이상 2짝), 겹치면 기기 사이 가운데, 150 미만 틈은 옆 장에, 나머지 약 500씩.
  싱크볼 구멍 아래 스테인리스 볼(깊이 200), 쿡탑 구멍에 검은 유리판(`fan`)
  상부장(머리줄 "상부장" 체크 `_3d.upper`, 처음엔 끔 — 파일에 upper:true일 때만 켬(2026-11-21), 하부장 체크와 무관, `_3dSetupGL` 5번째 인자): 미드웨이마다(`upSpans`, 바닥부터·판 제외) 그 벽 구간 위(미드웨이 윗변부터),
  미드웨이가 없으면 상판마다 가장 긴 `backs`(맞붙은 변 제외, 600 이상) 위 `_3D_UPGAP`(600). 깊이 `_3D_UPD` 350·높이 `_3D_UPH` 700, 도어 `_3dDoorSplit(L,[])`, 하부장 몸통·도어 배열에 같이(`furnDraw`)
  조각 구분(`_3dGetType/_3dSetType`, 도형 `piece3d` = top|obj|mid|panel(하부판, 예전 front|side)|etc(목록 이름 "삭제" = 3D에서만 안 그림), 선 조각은 선마다, 기본 = 폭 300 미만 etc·나머지 top,
  오브제 obj(2026-10-27, 선반·벤치 등 가구 아닌 상판) = 상판처럼 그리고 끌기·위아래(pos3d)도 같지만 하부장 없음·`backs`(미드웨이·상부장 자리) 아님,
  그 변(`ed.obj` = tops 항목)에 붙은 전면판·측판은 바닥부터가 아니라 오브제 밑면에 매달림(y = y0-Hm, 판의 mid3d.y0 무시) → tops 항목 `hang` = 매달린 판 높이,
  Shift 위아래의 바닥 맞춤 = 판이 바닥에 닿는 높이(`drag.vertTop.hang`), 3D 창 왼쪽 서랍 `_3dPiecePanel` — 아래 "3D 디자인"의 양옆 탭):
  미드웨이 = 상판 뒷변(`backs`: 앞면 아닌 300 이상 변, 긴 것부터)을 따라 상판 위에 세운 판(긴 변=벽 따라·짧은 변=높이·앞면 무늬), 기타 = 안 그림.
  도면 글자(2026-11-03 사용자 요청): 머리줄 "도면 글자" 체크(`_3dOpts.notes`, 기본 켬) → `_3dBuildScene`이 조각 무늬 캔버스에 `_3dDrawNotes`(글자 가운데가 조각 외곽 안인 note만, 높이 fs×1.5mm, 흰 테두리) — 조각과 같이 옮겨지고 PNG에도 들어감
  머리줄 "상판만 / 상판+미드웨이"(`_3d.mode`, `_3dSetMode`). 하부장·상부장·도면 글자 체크·보기 방식은 `_3dOpts`(창 닫아도 유지, 도면 파일 `view3dOpts`, `_3dOptsLoad` — 불러오기·새로만들기에서)
  — 3d-design 브랜치의 `view3d`(가구 디자인)와 다른 키
  조각 구분 목록은 한 줄씩(번호·크기·종류 버튼 + 옮겼으면 ↺ = 그 조각 pos3d·mid3d·midFace 지움)만 — 자리·방향·높이·무늬 조절은 모두 3D 마우스(목록 조절 버튼은 없앰)
  미드웨이 자리 손으로: 도형(`_3dKey`) `mid3d={edge:'상판도형id:변번호', off:mm, swap}` (끌기로 정함, `scene.edges` = 모든 상판 변). 장면이 지금 자리를 `pc.mid`로 돌려줌.
  판 면에 붙이기(2026-10-27): 그린 판·미드웨이마다 평면 네 변을 `allEdges`에 `{id:'p도형id:i', pan:true, y:그 판 아랫변, n:판 바깥}`으로 넣음 → edge가 'p…'면 그 판 다음에 그림(`_3dPanelOrder`),
  자동 자리·`_3dMidContact`에는 안 씀.
  판 밑에 매달기(2026-11-02 사용자 요청 "오브제 밑 띠판, 그 밑 양쪽 서랍판"): 판마다 밑변 `{id:'b도형id', a:W0, 판 변 방향·법선 그대로, len:Lm, y:yA, pan, bot, bobj(오브제 tops 항목), hb(오브제 밑면→이 판 아랫변)}` →
  edge가 'b…'면 같은 면으로 그 판 아래(y = yA−Hm, Hm ≤ 바닥까지), 오브제 hang = hb+Hm. `_3dDragTarget`은 bot 변을 그 높이 평면에서 재고(5 우선), 방향은 지금 swap 그대로(자동으로 세로로 돌리면 서랍판을 가로로 못 붙여서 없앰).
  판 테두리 선(분절선, `ln`)은 앞(F)·뒤(W) 두 넓은 면 모두에(예전엔 F면만이라 바깥 무늬 면에서 이음이 안 보였음) off는 변 밖으로 넘어도 됨(끝 min(20,len/2,Lm/2)만 걸치면). 끌기 자석 `_3dMagnet`(변 끝·상판 꼭짓점·다른 판 모서리 `midInfo.c`, 변에서 1500 안) + 기준선,
  Shift 위아래(drag.vert)도 바닥·상판 윗/밑면·다른 판 yA/yB에 맞춤
  졸리컷·고스라 3D(2026-10-27, `_3dSetupGL`의 `onMark(jMarks|gMarks,a,b)` = 도면 변 가운데가 표시 선 위+평행): 상판 바깥 둘레 변마다
  졸리컷 = 밑면을 두께만큼 안으로 당긴 45° 경사면, 고스라 = 윗모서리 `_GOS_C`(3mm) 45° 깎기. 판(미드웨이·전면판·측판)은 도면 사각형 변 → 위/아래/시작/끝(uv와 같은 대응),
  바깥면(무늬 면 `fc`, 양면이면 W)은 온전·안쪽면은 졸리컷 끝만 tm 짧게(→ 양 끝 45°), 윗변 졸리컷이면 바깥면을 tm 위로(상판 졸리컷과 맞물림), 아랫변은 안쪽면을 tm 올림. 면은 `q4`(법선 = 판 가운데 반대)
  끌기: mousedown에서 `_3dRay`(화면 → 광선, `_m4Inv`·`_3d.M`) + `_3dPickMid`(미드웨이 상자 `R.midInfo`) → 끄는 동안 `_3dDragTarget`(상판 윗면 평면 교점 → 가장 가까운 상판 변, 커서 가운데)
  노란 테두리 미리보기(`_3d.prev`, `_3dMidBox`) → 놓으면 `mid3d` 저장 후 `_3dRebuild`
  미드웨이 자동 자리(mid3d 없을 때): `_3dMidContact` = 도면에서 상판 변(`ed.o` = 옮기기 전 자리) 바깥쪽에 붙은 미드웨이 변 중 가장 길게 겹친 것 → 그 변·위치(s0),
  붙은 축 = 벽 따라, 다른 쪽 = 높이, 높이 > `_3D_TALL`(1000)이면 바닥부터(`floor`). 안 붙었으면 예전처럼 뒷변(`backs`)에 차례로.
  `mid3d.floor`/`pc.mid.floor` = 바닥부터 세움: `_3dFloorEdge`(법선 뒤집어 상판 바깥쪽, y=0). 끌기 `_3dDragTarget`은 윗면·바닥 두 평면 중 가까운 변(상판 위를 가리키면 윗면) → `floor`.
  `swap` = 기본(긴 변이 벽 따라)과 다른지
  위아래: `mid3d.y0`(바닥에서 아랫변 mm, 없으면 바닥 0/상판 윗면) — Shift+미드웨이 끌기(`drag.vert`, `_3dVertH` = 누를 때 시선 수평 방향을 법선으로 한 세로 평면과 광선의 높이, 0·topY에 맞춤).
  오른쪽 클릭은 y0 유지, 새 자리로 끌기는 y0 지움
  무늬 면: 도형 `midFace`(0 = 앞(상판 쪽 F면), 1 = 뒤(W면), 2 = 양면, 없으면 `_3dFaceOf` 기본: 미드웨이 0·판 1, mid3d와 따로 — 자동 자리 유지), `_3dFlipFace` = 더블클릭(`_3D_FACES`). "처음 배치로"는 안 지움
  하부판(2026-10-28 전면판·측판을 합침, 사용자 확정): `piece3d` panel(예전 파일의 front|side도 `_3dIsPanel` = 하부판, 목록 버튼은 "하부판" 하나), 미드웨이 고리에서 같이 그림(상판만 보기에서도) — `_3dPanelEdge`(상판 변 그대로·y=0 → 바깥면 = 상판 끝, 두께만큼 안쪽), 높이 ≤ 상판 밑면(`ed.y0`, 하부장 끄면 안 그림).
  자동 = `_3dMidContact`, 없으면 판 길이(상판 밑면 높이에 가까운 치수 = 높이, 나머지 = 길이)와 가장 비슷한 변(같으면 앞면 변 먼저), 벽 변(`ed.wall` = 미드웨이가 붙은 변)·맞붙은 변(`ed.joint`)·이미 쓴 변(`usedP`)·판 면(pan) 제외, 변 가운데.
  판 높이 축 = 상판 밑면 높이에 가까운 치수. `pc.mid.panel`/`midInfo.panel` → 끌기 미리보기도 `_3dPanelEdge`(바닥 라인 판정 무시, 항상 바닥부터)
  하부판 나눠 붙이기(2026-11-21 사용자 요청 "아일랜드 하부판 여러 개"): `_3dSetupGL`의 `pChain`(mid3d 없는 하부판) = 상판 변에 붙은 판(`_3dMidContact`) 뿌리 + 도면에서 그 판들에 맞붙은(상자 변 3 안·겹침 50 넘게) 판을 차례로 →
  같은 상판 변 도면 틀(`e.o`)로 s(변 따라)·d(상판 변에서 바깥 = 상판 밑면에서 아래로) → 상판 밑면에 매달아(y = 밑면 − d1, 바닥 밑은 자름, 오브제면 hang), 변 범위 절반 넘게 벗어나면 안 이음.
  붙은 판 하나도 이제 바닥부터가 아니라 상판 밑면에 매닮(키가 밑면 이상이면 예전과 같음)
  판 돌리기(2026-11-21 "360 돌리기"): 미드웨이·하부판 오른쪽 클릭 = `mid3d.rot`(0~3, 판 면 안 90°×n, swap = 돌리기 전 기준, `c` = 처음 돌릴 때 가운데 [변 따라, 높이] → 세웠다 잘려도 제자리),
  `_3dSetupGL`이 rot 홀수면 along을 바꾸고 `uv()`·졸리컷 변(jTop/j0/jBot/j1)을 rot만큼 돌림, `pc.mid`/`midInfo`에 rot → 끌기·위아래 끌기 저장에도 rot 유지
  가구 배치 모드(2026-11-21 사용자 요청 "가구가 계속 클릭돼서 상판 옮기기 불편"): 머리줄 체크 `#v3d-fedit` → `_3dFurnEdit`(3D 열 때마다 꺼짐, 파일 저장 안 함) — 꺼져 있으면 `_3dPick`이 가구 칸(unit/upper)을 안 잡음, 끄면 고른 칸 풀기
  판 조립 숫자 칸·면 클릭 붙이기(2026-11-21 사용자 확정 "클릭 붙이기 + 숫자 칸", 아일랜드 띠판·서랍판·옆판): 고른 조각(`_3d.sel`) → 위 가운데 `#v3d-pbox`(`_3dPBox`, `_3dRegeom` 끝·mousedown·mouseup마다, 칸 입력 중이면 안 바꿈)
  — 판: 붙은 면 이름(N번 앞/뒤/왼쪽/오른쪽 면·판 옆면·판 밑), "왼쪽에서"(화면 기준: 변 방향이 화면 오른쪽(`_3dScrRight` = cam.yaw)을 보면 off 그대로, 아니면 L−off−Lm)·"바닥에서"(y0) 칸, ⇤·가운데·⇥·⤒ 상판 밑에(`_3dUnderY`)·⤓ 바닥에·↻ 90°(`_3d.rotSel`)·무늬 면
    → `_3dPSet(key,patch)` = pc.mid 지금 자리 + patch를 mid3d로(saveHistory). 상판·오브제: 윗면 높이 칸(pos3d.dy)·돌리기
  — 📌 면 눌러 붙이기: `_3d.attach`(= 누를 때 sel) → 마우스 올림 `_3dFaceHit`(상판 변 옆면 0~윗면, 판 옆면 'p' 변 yA~yB, 100 미만 좁은 면·'b' 제외) → `_3dAttachPlan`(누른 점에 판 가운데, 면 끝·같은 면 다른 판 끝·상판(위 판) 밑면·바닥·같은 면 판 위아래 변에 tol 맞춤,
    아직 손으로 놓은 적 없는 판은 swap false·rot 0 = 긴 변이 면 따라) → `_3dAttachPrev` 노란 테두리 → 누르면 mid3d{edge,off,swap,rot,floor,y0}, 오른쪽 클릭·Esc = 취소
  — 높이를 손으로 정한 판(`fixY` = mid3d.y0 있음)은 상판 밑면·위 판 높이로 자르지 않고, 오브제·판 밑에 매달기 대신 그 높이 그대로(오브제 hang은 반영)
  — 방향키 `_3dSelNudge`(가구 칸 고른 게 없을 때): 판 ←→ = 화면 기준 off, ↑↓ = y0 / 상판 = 화면 방향에 가까운 축으로 pos3d (10, Shift 1)
  (2026-11-21 2차 사용자 요청) 하부판 대기 자리: 손으로 안 붙였고(mid3d.edge 없음) 도면에서 상판에도 안 붙은 하부판(`stg`) = 자동 변 고르기 대신 상판들 앞쪽 바닥 한 줄(`stage` = lo, zh+700, 폭 넘으면 450 앞 줄)
    긴 변 가로·n=(0,−1)(무늬 면이 +z), 대기에서도 mid3d{edge:null,rot}로 돌리기. 목록 종류 단추: 하부판 = mid3d·pos3d 지움(→ 대기), 상판·오브제 = 다른 상판들 오른쪽 600 옆·위 끝 맞춤 pos3d
    맞춤 약하게: `_3dMagnet`·`_3dSnap`·`_3dAttachPlan` tol = max(5, cam.d/260), Alt = 맞춤 없음(`_3dDragTarget(m,ray,free)`, 상판 끌기, 붙이기 hit.free). 판 끌어 옮기면 정해 둔 y0 유지(밑변 'b' 제외)
    거울상 막기(2026-11-21): 판 `mir` = 무늬 면(fc 0 = F면은 −n 방향, 1·2 = W면은 +n 방향으로 봄) 앞에서 변 방향 u가 화면 왼쪽이면 true → `uv()`가 a를 먼저 뒤집고 졸리컷 시작·끝 변도 맞바꿈 (도면 그대로 보이게)
    사각형 아닌 판(선 조각): 외곽(pc.loops.outer)을 uv 역변환으로 판 면 (s,y)에 → 넓은 두 면 = 무늬(투명 = 따낸 자리) 양쪽, 둘레마다 옆면(법선 = 다각형 바깥)·분절선, 졸리컷 경사는 사각형 판만
  하부장 높이(2026-11-21): 머리줄 "높이" 칸 `#v3d-h` = `_3dOpts.h`(view3dOpts에 저장, 200~1500) → `_3D_H`(상판 윗면, 기본 900)를 바꿈(`_3dOptsLoad`에서도)
    상판마다(2026-11-21 사용자 요청 "상판 모듈별로"): 상판 도형(`_3dKey`) `h3d`(200~1500, 오브제 제외) → `_3dSetupGL` 상판 고리의 `HH`(없으면 `_3D_H`), tops 항목 `hh`(Shift 위아래 맞춤 `drag.vertTop.hh`).
    숫자 칸 `#v3d-pb-hh`(상판, dy=0일 때 — dy가 있거나 오브제면 예전 "윗면 높이" = dy), 머리줄 값과 같게 치면 h3d 지움, "↺ 기본 높이"
  상판 자리 손으로: 도형(`_3dKey`) `pos3d={dx,dz,rot,dy}`(rot = 조각 상자 가운데 기준 90°×n, dy = 900에서 위아래 mm — Shift+상판 끌기 `drag.vertTop`,
  0·바닥에 맞춤·바닥 밑 안 감, dy≠0이면 그 조각 하부장 안 그림 = 주방 상판이 아닌 선반·테이블 등), `_3dSetupGL`이 외곽·구멍·윗면 사각형·하부장에 적용, `R.tops[]={key,loops,y,pos}`.
  마우스(`show3D`): 왼쪽 = 조각 위면 선택(`_3d.sel`) + 끌기(`_3dPick` → 상판은 `_3dPlane` 평면 교점 차이 + `_3dSnap`(다른 상판 꼭짓점 x/z tol 안 맞춤) → `pos3d`, rAF로 `_3dRegeom`
  = 버퍼만 다시(텍스처·GL 프로그램은 `_3dGLC`에 캐시), 미드웨이는 미리보기 → 놓을 때 `mid3d`), 빈 곳 = 돌리기, 오른쪽/가운데/Shift 끌기 = 옮기기,
  기준선 `_3d.guide`(선 정점 배열, 끄는 동안만, mouseup에서 지움): `_3dSnap`이 맞춘 꼭짓점 쌍을 잇는 선(높이 다르면 세로로 이음), Shift 위아래는 900·바닥·다른 상판 윗면에 맞추고 `_3dHGuide`(그 높이 수평 테두리)
  → `_3dLabels`가 `#v3d-labels` 위 SVG 분홍 점선으로 그림(WebGL 선은 1px라 안 씀),
  되돌리기(`_3dUndo`, Ctrl+Z는 3D `onKey` capture에서, 머리줄 `#v3d-undo`): 편집 화면과 같은 `_hist` — 끌기는 mousedown `drag.snap`(`_3dHistSnap`)을 바뀌었을 때 mouseup에서 기록,
  돌리기·무늬 면·조각 구분·↺·처음 배치로는 `saveHistory()` 먼저. 창 열 때 `_3d.histBase`까지만 되돌림, undo 뒤 `_3dRebuild`(도형 객체가 바뀜)
  오른쪽 클릭(안 움직임) = 상판 rot+1 / 미드웨이 swap, R 키 = 선택 조각 돌리기, 올림 `_3d.hover` 파랑·선택 주황 외곽선. "↺ 처음 배치로" = `_3dResetLayout`(pos3d·mid3d 지움)
  조각 번호표 `_3dLabels`(`_3dRender` 끝마다): `#v3d-labels`(캔버스 위 HTML, 이미지 저장엔 안 들어감)에 목록 번호(scene.pieces 순서) — 상판 윗면 안쪽 점·미드웨이/판 상자 가운데, 올림 파랑·선택 주황.
  목록 줄 `data-row` 올림 → `_3d.hover`, 번호·이름 `data-pick` 누르면 `_3d.sel`, 3D 올림·선택이면 목록 줄 배경 강조
  유광(2026-10-28): `_3dGloss(도형)` → `_prodGloss(제품 구분 이름)` = 제품명·몰 상품명/영문명에 유광|폴리시드|루시도|polish|gloss… → 1, 라파토|lappato|반광 → 0.5, 그 밖 0 → 장면 조각 `gloss` → 그리기 `d.gloss`.
  셰이더 `uG`(광택)·`uE`(눈 위치)·`vW`: 무늬 면(상판 윗면·미드웨이/판 무늬 면, 옆면은 0.6배)에만 하이라이트 + 반사 광선이 높이 2600 천장 일자 라인 조명(z 방향, 폭 약 70, x 2800 간격 — 사용자 요청 "조명이 너무 많다")에 닿는 곳 밝게 + 프레넬. 다른 면은 uG=0
  카메라 yaw/pitch/거리(`_3dSetView` iso/top/front), 좌표 X=도면 x·Z=도면 y·Y=위. 사진 불러오는 중이면 300ms마다 다시(`_3dRebuild`). PNG 저장은 `_pickSaveFile('img')`
- **3D 디자인**(2026-10-28 개발판 `3d-design.html`에서 만들어 본판에 합침 — 브랜치 `3d-design`·작업 폴더 `..\simplecad-3d`는 그 기록):
  - 설정 `_3dStyle`(`_3dStyleDef/_3dStyleLoad/_3dUp`) = 도면 파일 `view3d`: lower/upper {door 색, design, finish 마감 id, upper.same}, handle {type,color,len,dir}, prod(제품 바꿔 보기), upOff(상부장 높이), unitDel(지운 칸), upDel(예전)
  - 3D 창 양옆 서랍: 왼쪽 조각 구분 `#v3d-side-l`·오른쪽 디자인 `#v3d-side-r`, 가장자리 세로 탭 `#v3d-tab-l/r`(`_3dSideOpen/_3dSideSet`, localStorage `scd_3d_side_l/r`, 처음은 왼쪽 열림·오른쪽 닫힘)
  - 디자인 창 `_3dStylePanel`(`_3dMatUI`): 하부장/상부장 도어 탭 → 스케치업 재질 창 모양(미리보기 + "선택" 브랜드·분류 견본 / "편집" 직접 색).
    "선택" 위 검색 칸 `#v3d-fq`(`_3dMatUI.q`, 2026-10-28): `_3dFinGrid(list,q,cur)` = 검색어 있으면 모든 브랜드에서 이름·품번·브랜드·분류(+유광)에 단어 모두 포함 + 견본 아래 이름·브랜드. 칠 때는 0.15초 뒤 `#v3d-fgrid`만 다시(포커스 유지, `window._3dFinGridRefresh`), 분류 고르면 검색 지움.
    무늬 도착 `_doorTexArrived`: 0.12초 묶어서, 지금 도어에 쓰는 무늬일 때만 `_3dRegeom`, 창은 견본 칸만(쓰는 무늬 + 검색 칸 안 쓰는 중이면 창 전체).
    견본 `_doorFinishSwatch`는 결 이미지 왼쪽 위 256px를 96px로 줄여 그 위에만 색 입힘(`_doorFinishCanvas` 원본 크기 계산은 3D 텍스처용) 몸통·걸레받이는 고르지 않고 `_3dAutoBase`(Lab ΔE `_rgbLab`로 가장 비슷한 단색, 걸레받이 78%)
    도어 디자인 `_3D_DESIGNS`(민자·쉐이커·슬림·루바·리브드·그루브, 상부장 유리장), 손잡이 `_3D_HANDLES`(없음·바·노브·둥근 노브·라인·골라·엣지·매립형 + 길이·방향·색 `_3D_HCOL`), 그림 단추 `_3dIcon`
    제품 바꿔 보기 = 윤현몰 사진 2칸 격자(같은 두께·검색) → 3D 무늬만(`_3dProdId` → `_slabImgById`) / "도면에 적용"
  - 마감 `_3D_FINISH`(id·name·grp·rgb·tex·tw·th·raw·gloss·code·brand) · `_3D_BRANDS`(ARCKIT·한솔 스토리보드·영림 인테리어필름) · `_3D_GRPS`, 무늬 `door-tex/*.js`(`_doorTexImg`, `_doorFinishCanvas` 색 입힘·raw는 그대로 거울 반복).
    브랜드 더하기 = `_3D_BRANDS` + `_3D_FINISH` 항목 + door-tex 이미지 (한솔·영림은 사용자 PDF 카탈로그에서 Windows.Data.Pdf로 쪽을 그려 견본을 잘라 만듦, ARCKIT은 사용자 .skp 재질)
  - `_3dSetupGL` 가구: 도어 `door(F,P,Q,dy0,dy1,nx,nz,design,isUp,side,ang)`(손잡이 쪽 `_3dHandleSide`, ang = 열린 각도 → 두께 18 + 경첩(손잡이 반대쪽 앞 모서리) 축 회전),
    몸통 = 도어마다 칸 `bay`(뒷판·옆판·밑판(상부장 윗판) + 선반 2단, 하부장 깊이 `depthIn`, 앞면 변 없는 조각은 예전 외곽 벽,
    싱크볼 구멍 상자와 겹치는 하부장 칸은 높이를 볼 바닥 밑(상판 밑 −202)까지만 + 윗판 — 구멍으로 옆판·선반이 안 보이게, 2026-10-29) → `R.unitInfo`(key 하부장 `L상판id:변:번호`/상부장 `U자리key:번호`)
    `_3dPick` kind 'unit'(하부장 칸)/'upper'(상부장 칸, 끌면 그 상부장 전체 위아래 → `upOff[자리key]`, 자석·기준선) → 누르면 `_3d.selUnit` 노란 테두리 `_3dUnitOutline`, Delete = `_3dUnitDelete`,
    더블클릭 = `_3dDoorToggle`(0↔90°, 파일 저장 안 함). 되돌리기 `_3d.fOps`(지우기·상부장 높이, 그때 `_hist` 길이) — `_3dUndo`가 먼저 처리, "가구 처음대로" = 모두
  - 가구 칸 객체(2026-10-31): `_3dStyle.units[칸 key] = {o:[x,y,z] 옮긴 mm, t:종류}`(`_3dUnitOf/_3dUnitSet`, 0·swing이면 지움). `_3dSetupGL`이 칸마다 `uMark()` → 몸통·걸레받이·앞면 그림 → `uShift(m,o)`로 그 정점만 옮김, `unitInfo`에 o·축(ux,uz,nx,nz)
    옮기거나 지운 하부장 칸의 원래 자리 = `bay(...,slotOnly)` 빈 칸(뒷판·양옆·어두운 바닥, 옆 칸과 같은 면이면 깜빡여서 1mm 안쪽, 싱크볼 밑이면 볼 밑 `byt`까지 + 천장), 옮긴 칸은 온전한 높이 + 윗판(법선 위)
    하부장 칸 = `oneUnit(uk,A,u,n,s0,s1,깊이,손잡이 쪽)`. 깊이(`depthIn`) > 800이면 절반(2026-11-02): 닿은 맞은편 변(`depthIn.hit`)이 앞면 변이면 그쪽도 절반이라 그대로,
    아니면 뒤 줄 칸 key `…b`(앞 선 = 깊이 끝, u·n 반대, 문은 뒤쪽). 가구통 모서리 선 `furnDraw.line/uLine`(bay 12모서리, 몸통 색 ×0.32, 제자리 칸은 도어·상판에 가려 빼낸 칸·빈 자리에서만 보임)
    고르기 `_3d.selUnits`(Ctrl+클릭 여러 개, `_3dSelSet`/`_3dSelOutline`, 마지막 = selUnit), 위 가운데 종류 막대 `#v3d-utype`(`_3dUTypeBar`: `_3D_UTYPES` 버튼·↺ 자리·삭제)
    끌기 `drag.um` → `_3dUnitMove`(누른 칸 축으로 옆 a·앞뒤 b, 작은 쪽 < 큰 쪽 0.5면 0(Alt 자유), 다른 칸·상판 외곽 상자 옆면/앞뒷면·처음 자리 tol 맞춤 + 기준선 / Shift = 위아래 `_3dVertH`, 바닥·칸 y0/y1·상판 높이),
    방향키 `_3dUnitNudge`(←→ 화면 기준 옆, ↑↓ 위아래, 10/Shift 100), Delete = 고른 칸 모두. 되돌리기 fOp `{t:'units',prev:JSON}`·`{t:'del',keys}`. 예전 상부장 전체 높이 `upOff`는 읽기만(끌기는 이제 칸 단위)
  - 칸 종류 앞면 `uFront`(`_3D_UTYPES`, 안 부품 도우미 `bx` 상자·`cav` 안쪽 통·`mvOut` 같이 빠짐, LF/UF에 body·sink 배열도): 하부 swing·drawer(3단 24/36/40%, 열림 위 0.4·가운데 0.68·아래 1, 서랍 통 `drawerBox`)·
    pullout(앞판 + 바구니: 옆판·뒤 틀·선반 3단·투명 난간)·dish(문 위 조작부 띠 `hopt.band`·안쪽 스테인리스 `hopt.inner`, 아래 축으로 내려옴, 안 스테인리스 통 + 랙 2단(아래 랙 0.7·위 0.35 빠짐))·
    oven(빌트인: 위 막음판 60 · 조작부 85(표시창·다이얼) · 오븐 문 design 'oven'(스테인리스 틀+검은 유리+검은 막대, 아래로) + 검은 오븐 칸·선반 · 아래 서랍). 서랍류는 `bay` 선반 없음(noShelf) /
    상부 swing·flap(위 축으로 들림)·fold(두 짝, 아래짝 `fold2` = 위짝 아래 모서리 따라 반대로 접힘)·slide(앞 22 띄운 짝 + 뒤 짝이 옆으로 밀림 `slu`, 매립 손잡이). `door(...,mode,hopt,ext)` = 열리는 방식·손잡이 덮어쓰기·거리
  - 첫 화면 `_3dIntro`(약 1.8초): `_3d.anim={t}` → `_3dAnimPh()` s(상판 3D 자리로 미끄러짐·돌기)·r(900으로 올라감, 하부장 같이 자람)·m(미드웨이·판 눕힌 데서 세움, 정점 보간)·g(상부장 내려앉음), 시점 위에서 → 비스듬히, 누르면 끝
  - 닫을 때 `close3D(true)`(✕ 버튼만, show3D 안의 close3D()는 바로) → `_3dOutro`(2026-10-29): `st.closing`, 번호표·양옆 서랍 흐리게, t 1→0(약 1.5초), 시점 지금 → 위에서(t=0 장면), 끝나면 창 opacity 0.25초 뒤 close3D. 누르면 바로(`animStop`), 닫는 중이면 `_3dIntro`는 멈춤
  - door-tex 이미지는 외부 카탈로그 자료 — 공개 저장소에 올려도 되는지 사용자 확인 후 올림
- 가공비: `calcCost` / 저장·불러오기: `_makeProjectData`, `loadProject`(.ceramic=JSON, 단가 포함) / DXF: `importDxf`
- 단가: 브라우저 localStorage(`scd_prices_<등급>`), 다른 PC로는 `exportTierPrices`/`importTierPrices`
  - 단가 설정 이름·추가(2026-11-24 사용자 요청): 이름 `tierName(id)`(localStorage `scd_tier_names`, 기본 `_TIER_DEFNM`), 버튼 더블클릭·"✏ 이름" = `renameTier`,
    "＋ 설정 추가" `addTier` = 지금 설정 값을 복사한 `{id:'tN',pf:'tN-'}`(`scd_tier_extra`, `_tierMakePanel`이 커스텀 판을 복제·`TIER_PREFIX`에 더함, 시작 때 `_tierInit`), "－ 빼기" `delTier`(기본 다섯 개는 못 뺌).
    단가 파일에 `names`·`extra`도. 설정 목록은 `_tierIds()`(하드코딩한 다섯 개 목록 쓰지 않기)
- 객체 1식 금액(2026-11-24 사용자 요청): calcCost가 객체(groupRole main rect·원 타공·타원 타공) 둘레 가공 표시를 안 셈 — 같은 groupId(`_objG`) + 손으로 객체 변·라운드 코너·원 둘레 위에 그린 것(`_onObjEdge`, 가운데 점 ±2~3mm). 객체 코너 R도 R 구간 금액 없음(groupId 있는 rect는 원래 제외)
- 오른쪽 가공비 패널 순서 = 왼쪽 도구 묶음(2026-11-24 사용자 요청 "기준은 좌측"): ① 커팅 가공(rect·holef·holeo·circlecut·line) ② 객체 삽입(sink·cook·dish·food·doma1~3) ③ 추가 가공 ④ 기타 비용 ⑤ 합계(`s-cut`·`s-obj`·`s-add`·`s-other`) ⑥ 단가 설정.
  단가 칸은 `_EXTRA_PRICE_ROWS` IIFE 끝에서 판마다 "객체 삽입" 제목을 넣고 sink·cook·food·doma 줄을 옮김("선 커팅" 글자 = "직선 커팅"). 새 가공 줄도 이 순서에 맞춰 넣기
- 용어: 화면 글자는 "절단" 대신 "커팅"(2026-11-24 사용자 요청 — index.html·patch-notes.js 모두 바꿈, 새 글자도 커팅)

## 도면 표기 규칙 (사용자 확정)
- (도면화·원판 배치) 변은 모두 조각 색 실선, **밑면연마 = 변에서 재료 쪽 50mm 띠에 주황 45° 빗금**(`_expHatchBand`, `_GRIND_MM`),
  **고스라 = 검정 ▲** (꼭지점이 방향), **졸리컷 = 빨간 ★·선**(뒷면, 기본) / **앞면 졸리컷 = 속 빈 ☆**(jollymark `front:true`, 2026-11-20 사용자 요청:
  졸리컷 도구 보조 칸 `#jollycut-sub` `setJollyFace`(`_jollyFront`) + 속성 칸 `setJollyFaceSel`(여러 개 선택도), `drawStar(...,hollow)`, DXF `star(...,hollow)` = 닫힌 폴리선, 범례는 앞면이 있을 때만 둘 다, 3D는 밑모서리에서 안쪽 위로 깎음) — 편집 화면은 예전 색 그대로(고스라 빨강, 졸리컷 파랑)
  - ★·▲ 크기 = 예전 크기 × `_MARK_K`(0.5, 2026-11-02 사용자 요청 — 1/4은 너무 작다고 해서 2배로) — 편집 화면·도면화·DXF 모두, 범례 견본만 예전 크기. ▲ 클릭 판정은 최소 7px
  - 사각/선 절단 조각 변: 바깥에서 조각 안쪽을 향함 / 싱크볼·쿡탑 변: 타공부 안쪽에서 선을 향함 (밑면연마 띠 방향도 같음, `_gosraDir`)
  - ▲ 자리는 `_gosraSym(m)`: 곧은 변 = `_gosraDir`, 라운드 코너·원 둘레(`_findCornerAttach`) = 호 가운데 점·재료 쪽 방향(2026-11-03) — 편집 화면·`_markSym`·도면화·DXF 공통
- 조각마다 색은 **외곽선만**(안은 흰색, 음영 없음 — 도면화 1쪽·원판 배치 사진 없을 때), 치수는 조각 색 화살표 치수, 정수 표기, 글자는 항상 바로 서게
- 선 각도(`_lineAngleMarks` → `_drawAngleMarks`, 편집 화면·도면화 공통, DXF는 `_dxfCollect`에서 SC-DIM ARC+TEXT, ° = `%%d`): 선 두 개가 만나는 점마다 사잇각 호+값(직각·일직선 제외),
  이어진 선이 없는 비스듬한 선은 시작점에서 수평 점선 기준 각도
- R값·Φ값은 대각선 지시선으로 빼서 어떤 선에도 글자가 걸치지 않게
- 조각 자동 번호는 상판 조각만(싱크볼/쿡탑/타공/다른 사각형 안의 사각형 제외)

## DXF 불러오기 해석 규칙 (오토캐드)
- 단위: `$INSUNITS` 따름. 단 인치/피트인데 환산 크기가 30m를 넘으면 mm 도면으로 보고 배율 1 (템플릿 탓에 인치로 저장된 mm 도면이 흔함)
- 폭 있는 폴리선 = 테두리/주석 → 무시 / 블록(INSERT)·글자·치수 무시
- 사각형 끝에서 끝까지 가로지르는 선(가장자리 60mm 초과 안쪽) = **접합부** → 조각 분할
- 변에서 60mm 이내 평행선 = 해치 경계 → 절단선 아님
- 조각 안 사각형: 라운드 → 싱크볼, 직각 → 안에 쿡탑 표기 글자(쿡탑·인덕션·하이라이트·가스·전기레인지·COOK·HOB, `cookRe`)가 있을 때만 쿡탑, 없으면 보통 사각 절단(2026-10-30 사용자 확정) / φ45 이하 원 → 수전 타공
- **해치 = 밑면연마**, **"OPEN" 글자 = 그 변에 밑면연마 + 고스라**
- 조각 이름: 조각 안(없으면 300mm 이내) 짧은 글자
- 닫힌 폴리선 사각형은 코너마다 라운드/모따기가 달라도 사각 조각(`corners`)으로

## DXF 내보내기 (`exportDxf` 창 → `buildDxf` / `buildDxfInForm`, 상단 "DXF 내보내기" 버튼)
- 길이 치수 = 진짜 DIMENSION(`dim()` → `{t:'DIM',parts,p10/p11/p13/p14,ang(0|90|null=정렬),txt}`): 그린 모양(parts)은 익명 블록 `*D n`(`_dxfDimBlocks`, 양식의 *D 번호 다음부터)에,
  치수 스타일 `SC-DIM`(`_dxfDimStyle`, 양식이면 DIMSTYLE 표 머리 71·340 목록도 늘림). 글자: 양식(R2000+) = 측정값 "<>"+앞뒤 글자, R12 = 값 그대로.
  모든 SC-DIM이 치수: `dimEnt(o,draw)`(draw로 그린 것 = 블록), `o.k` lin(0 회전/1 정렬) · rad(4, R·C 지시선 `leaderDim`, 곡선 근사 R, 치수선 도구 R) · dia(3, Φ 지시선·치수선 도구 Φ) · ang(5 3점, `angDim`: 선 각도·치수선 도구 각도).
  R/Φ/각도는 값만이면 글자 비움(오토캐드가 R·Ø·° 붙임), 모따기 C는 글자 그대로
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
  타공 → 가까운 상판 바깥 변 + 같은 조각 싱크볼이 있으면 가장 가까운 싱크볼 변까지도(같은 줄 여러 개는 이어서 간격, 2026-11-19), Φ값은 치수 없는 쪽 지시선
- 레이어 색·선 종류(`_DXF_LAYERS` = [이름, ACI, 트루컬러 420(R2000+), 선 종류], 2026-10-30 사용자 지정): `SC-GRIND` #F2F051 · `SC-DIM` #EB3324 · `SC-GOSRA` #D62E21 ·
  졸리컷 ★만 엔티티 색 #000000(ACI 7, 엔티티 `tc` → 420), 졸리컷 선·나머지 레이어는 예전 ACI. `SC-HOLE`(원 타공 + 사각 타공 rect) = 점선 `SC-DASH`(`_dxfDashPat(H)`, LTYPE 표에 추가)
- 해치 엔티티 `{t:'HATCH',pts,solid?,spacing,r12}`(92=3 폴리선 경로): 밑면연마 = ANSI31 45° 빗금(경계 = 띠 사각형), 졸리컷 ★(`star`)·고스라 ▲(`fillPoly`) = SOLID 채운 해치 한 개체.
  R12는 해치가 없어 `r12`(선·SOLID 목록)로 대신 씀, 엔티티 `only:'r12'|'modern'` = 한쪽 형식에만. 졸리컷 변 위 색 선은 안 그림, 밑면연마 띠 테두리 폴리선은 그림(사용자 요청 2026-10-30) —
  다시 불러올 때는 `SC-GRIND` 테두리 폴리선만 읽고 같은 띠의 HATCH는 건너뜀
- 쿡탑은 가운데에 `SC-NAME` "쿡탑" 글자(다시 불러올 때 쿡탑 표기로 읽힘)
- 레이어: `SC-PIECE` 조각 / `SC-CUTOUT` 싱크볼·쿡탑 / `SC-HOLE` 타공 / `SC-GRIND` 밑면연마 띠+해치 / `SC-GOSRA` 고스라 ▲
  / `SC-DIM` 치수(선+화살촉+글자) / `SC-NAME` 조각 이름 / `SC-NOTE` 도면 글자·화살표 / `SC-JOLLY` 졸리컷 ★ / `SC-TITLE` 표제란
- 다시 불러오기 호환: `SC-DIM/NOTE/GOSRA/JOLLY/TITLE`은 무시, `SC-GRIND` 띠는 해치처럼(밑면연마+고스라) 해석, 양식 블록(INSERT)은 무시

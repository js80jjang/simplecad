# 심플 캐드 (세라믹 상판 가공비 계산기)

세라믹 상판 도면을 그리고 가공비 견적·도면(PDF)·온장 배치를 만드는 **단일 파일 웹 앱**.
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
  — 검색은 한글·영문·사이즈, 여러 단어는 모두 포함. 고르면 제품명·사이즈 채움 + 온장 크기(`board-w`=긴 쪽, `board-h`)도 그 사이즈로(`_setBoardFromSize`)

- 온장 이미지: 같은 워크플로가 `tools/update_mall_images.py`(Pillow) 실행 → 몰 목록 이미지(= 온장 전체 사진 2:1, 몰에서 가장 큰 것이 1150×576)를 줄이지 않고 JPEG q86(`SPEC`, 바꾸면 전부 다시 받음, 장당 ≈90KB)으로
  `mall-img/<상품번호>.js`(`window._MALL_IMG[id]=data URL`)로 저장, `mall-img/manifest.json`에 원본 주소(같으면 다시 안 받음), 빠진 제품은 지움
  — 목록 이미지 폭이 600 미만(6mm 제품은 몰 목록 이미지가 150×75)이면 상품 페이지의 상세 이미지(`/image/detail/`, 대부분 1150×576, 비율 1.6~2.4일 때만)를 씀,
    manifest 값 끝 `|d` = 상세 이미지 확인함(다시 안 봄). mall-img 이미지가 바뀌면 sw.js `CACHE` 버전도 올림(설치 앱은 mall-img를 저장본 먼저 씀)
  — 쇼핑몰 이미지 서버에 CORS가 없어 바로 연결하면 도면화 캔버스가 막히므로 저장소에 받아 둠(사용자 승인: 공개 저장소에 올려도 됨)
  - 앱: `_slabImgFor(제품 이름)`이 `<script>`로 불러옴(`_updateBoardQty`에서 미리), `_boardLabel(장)`=조각에 붙인 제품/첫 제품,
    `_drawSlab`로 온장 배치 창·도면화 2쪽에 채움 — 사진은 실제 밝기 그대로(옅게 하지 않음), 남는 부분만 검정 32%로 어둡게,
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
    그룹(싱크볼 등)·이어진 선 조각 전체가 같이 바뀜, 지정하면 저장된 온장 배치는 초기화. 제품 이름 바꾸면 도형도 따라감(`_setProdName`), 제품 빼면 첫 제품으로
  - 편집 화면: 제품 2개 이상이면 조각을 제품 색으로 옅게 + 왼쪽 아래 제품명(`_drawProdTints`), ●에 마우스 올리면 그 제품만 진하게(`_hoverProd`). 도형 속성창의 제품 선택은 없앰
  - 온장 배치: 제품별로 장을 따로(`_packBoardItems` 그룹 = `_itemProd`), 장 머리글 `_boardTitle`="온장 N · 제품명", 온장 사진도 그 제품(`_boardLabel`).
    **온장 크기도 제품마다**: 제품 사이즈 칸에서(`_prodBoardSize`, 없으면 도구줄 온장 칸) → 장마다 `board.bw/bh`(`_boardDims`),
    배치 창·도면화 2쪽 칸은 가장 큰 온장 기준·장은 자기 크기로, 끌기·돌리기 한계는 그 장 유효 영역(`_bsArea`). 저장 배치는 `sig`(`_boardSizeSig`)가 같을 때만 복원
    도면화 1쪽 왼쪽 위·DXF 양식 글자는 제품마다 한 줄
- **온장 그대로 사이즈**(`_FULL_TXT`, 2026-10-27 사용자 확정 "배치 방향 기준"): 사각 조각 한 변이 온장 폭/길이와 같으면 후보(`_fullElig` → `item.full`, w/h는 실제 크기),
  **온장 배치에서 그 변을 온장의 같은 방향으로 놓았을 때만**(1600×3200 온장에 1600 변을 1600 방향으로) 온장 그대로 — 3200 방향으로 놓으면 보통 조각.
  `_placeDims(it,rotated,ew,eh)` = 배치 칸(그 방향은 ew/eh로 20 줄임, 자동 배치·오른쪽 클릭 돌리기·복원이 씀), `_pFull(p)` = 칸이 실제보다 작은 방향, `_pLabel(p)` = 크기 글자+표기.
  `_boardPiece`·`_3dWorldToBoard`가 그 방향 온장 끝까지 늘려 그림. `_fullBoardFit(s)` = 지금 배치(`_drawingBoards`)에서 도형 화면 상자 w/h 기준(캐시: calcCost마다 `_fullVer++`·저장 배치 바뀌면),
  `calcCost` 사각 절단에서 그 방향 양쪽 면 뺌, 도면화·DXF 치수 옆 표기 (편집 화면 치수는 그대로). 배치 창 닫으면 calcCost.
  자동 배치는 실제 크기로만 놓은 쪽이 장수가 적으면 그쪽(`_packBoardItems`). 예전 저장 배치(방향 상관없이 줄인 칸)는 같은 자리에 지금 규칙 크기로 복원, 겹치면 새로 배치
- 제품 수량 = 온장 배치 장수(자동, 읽기 전용 `pq-N`): `_updateBoardQty`(calcCost 끝에서 `_scheduleBoardQty`, 배치 창 닫을 때)가
  손으로 고친 배치(`_savedBoardLayout`)나 자동 배치에서 장마다 고른 제품별로 셈. **가공비에 곱하지 않음**(가공을 여러 번 하는 뜻 아님)
- 작업 정보 줄(도면 위 `#work-bar`): `site-info` 한 칸 "업체명/현장주소"(첫 '/' 앞=업체명, 뒤=주소, `_syncSiteInfo`/`_setSiteInfo`) →
  숨은 `company-name`(업체명)·`site-addr`(주소)에 나눠 넣음(저장 파일 company/siteAddr 그대로), 최근 목록 `scd_siteinfo_history`, 제품(`renderProductList`, 2개부터 `#prod-pop`),
  `deliv-date`/`deliv-time`(직접 입력 → `_normDate` 2026.10.28 / `_normTime` 14:00). 업체명·주소 최근 15개는 localStorage
  — 도면화·DXF에는 `_companySite()`("업체명 - 주소"), 저장 파일 이름은 `_saveBaseName()`(업체명-주소-20261021)
  — 저장 창 `_pickSaveFile(kind,기본위치,opts)`: 처음은 바탕화면(.ceramic)/문서(DXF), 그다음은 지난번 저장 파일 핸들(IndexedDB `scd-files`, kind별)의 폴더 + picker `id`.
    불러오기 `loadProject`도 `showOpenFilePicker`로 지난번 불러온 폴더('open', 없으면 'save' → 바탕화면), 없는 브라우저는 파일 칸 → `_loadProjectFile(file,핸들)`
  — "💾 저장"(`saveProject`, `#btn-save`, Ctrl+S) = 지금 파일 핸들 `_curFile`(`_setCurFile`: 열기 창으로 불러온 .ceramic·다른 이름으로 저장한 파일, 새로만들기·DXF·파일 칸 불러오기면 없음)에 창 없이 덮어씀(권한 `requestPermission`),
    없으면 "다른 이름으로 저장"(`saveProjectAs`, `#btn-save-as`, Ctrl+Shift+S = 예전 저장 창 → 고른 파일이 `_curFile`)
- 도형 kind: `rect`(x,y,w,h,rotation,cornerType/cornerSize,corners,groupId/groupRole/applianceType,pieceName,shapeNum,hideDims),
  `line`(x1..y2, DXF 곡선 근사면 arcR/arcMid), `circle`(cx,cy,r,holeType: faucet|outlet|cut), `arc`, `ellipse`,
  `grindregion`(밑면연마, inward, depth), `gosramark`(고스라, outward), `dimline`, `jollymark`,
  `note`(도면 글자: x,y,text,fs=도면화 px,color), `arrow`(화살표: x1..y2=촉, bend 휨, color — 그린 뒤 양 끝 점 끌기/길이 입력으로 크기 수정), `linkmark`(연결 표시: x1..y2 따라 물결 2줄, color) — 주석이라 조각/가공비/온장 배치에서 제외
- 싱크볼/쿡탑 = `groupRole:'main'` rect (라운드=싱크볼, 직각=쿡탑) + 싱크볼은 둘레 고스라 4개
- 사용자 그룹 `userGroupId`(`groupSelected`, 새 id는 쓰는 중인 것과 안 겹치게): 싱크볼·쿡탑 그룹(groupId)은 그대로 두고 그 전체도 사용자 그룹에 넣음.
  `getGroupShapes`는 사용자 그룹 + 멤버의 groupId 전체 + 그룹 사각 조각 안의 싱크볼·쿡탑(예전 파일) → 그룹째 끌면 같이 이동.
  싱크볼 크기 맞춤 `syncGroupShapes`는 groupId 멤버만
- 편집 화면: `redraw` → `drawShape`/`drawDims`/`drawNestDims`/`drawShapeNumbers` …
- 선 절단 도구 = 오토캐드 LINE 방식(`lineChain`, `_lineAddTo/_lineMouseUp/_lineKey/_lineOverlay`): 클릭 = 시작점 → 마우스를 움직이면 미리보기 선 + 동적 입력(`_lineDynInput`:
  선 옆 점선 치수의 길이 칸(파랑 선택 = 바로 치면 바뀜, 입력 중엔 친 글자), 시작점 수평 기준 점선 호 + 각도 칸, 커서 옆 "다음 점 지정 또는 길이 입력")
  → 클릭(또는 끌다 놓기, `_lineMouseUp`) = 그 점(직교·스냅 적용)까지 바로 선 / 움직이며 숫자 + Enter(`_lineKey` → `_lineTarget`) = 마우스 방향으로 그 길이
  (누른 채 숫자로 그렸으면 놓을 때 무시: `lineDown.nseg`), Tab = 지금 방향으로 길이·각도 입력란(`#line-pop`, 각도 칸 커서, 0°=오른쪽 반시계). 끝점에서 계속 이어 그림, 끝나도 도구 유지
  `300,-200`(상대, 위가 +)·`500<90`(길이<각도), 빈 Enter/Esc/오른쪽 클릭=끝, C=닫기, U=마지막 선 취소. 기본 직교(Shift=자유). 전역 mouseup의 `finalizeShape`는 line 제외
- 치수선 도구(`dimline`, `dimLineType` dist|r|phi|ang, `_dimSt`, `_dimClick/_dimPreview`): 길이 = 두 점(클릭 또는 끌기) → 마우스로 위치 → 클릭
  (`_dimBuildLinear`: 두 점 위·아래면 가로, 옆이면 세로, Shift 비스듬히. 저장 x1..y2=기준선, offsetMm(음수=반대쪽), e1/e2=실제 점까지 보조선 연장),
  각도 = 선/사각형 변 두 개 클릭(`_dimSegAt`) → 마우스 쪽 사잇각(`_dimBuildAng`, x1,y1 꼭지점·x2,y2 호 위 점·a0·sweep), R/Φ는 예전대로 원 클릭
- 판정 공통: `isInsideRect`(회전 포함), `_axisBox`, `_rightAngle`, `findEdgeContext`, `_lineBoundaryGroups`, `_gosraDir`
  - 공통 도우미(새 코드는 이걸 쓰고 같은 계산을 다시 쓰지 않기): `_rectXf/_rectCorners`(회전 rect 꼭짓점), `_isAnnot`(주석 도형 제외),
    `_nearestEdge`(트림·호버 변 찾기), `_isCutRect`(타공부 사각형), `_drawRLeader`(R·C 지시선 글자), `_ymd`(20261021), `_TOOL_SUBS/_TOOL_FOCUS`(도구 보조 칸)
- 선택: `hitTestAll`(조각 변의 밑면연마·고스라·졸리컷 = 우선순위 -1, 싱크볼 둘레 표시는 제외), `_markAreaHit`(밑면연마 빗금 띠·고스라 ▲ 안도 선택),
  마우스 올림 강조 `hoverShape` = `hitTestAll`의 첫 도형(클릭 결과와 같음): 고스라 진한 빨강 굵은 실선·큰 ▲, 밑면연마 빗금 칸 진하게+테두리, 졸리컷 진한 파랑, 도형 파란 테두리·채움
  (아무것도 선택 안 했을 때 올리기만으로 잡힌 선택(`_hoverSelected`)보다 강조색이 먼저)
- 트림 `doTrim`: rect는 `_trimRectGeo`(90° 단위 회전 = 보이는 대로 회전 없는 rect·코너 키 돌림, 그 밖 각도 = 꼭짓점 `_pts`) +
  `_trimRectEdges`(위→오른쪽→아래→왼쪽, 클릭 판정·교점·분해가 같은 방향)로. 잘린 구간에 겹친 같은 직선 위 선은 `_trimOverlaps`로 같이 지움
- 조각/배치: `_collectBoardItems` → `_packBoardItems` / `_restoreSavedBoards`, `showBoardLayout`, `renderBoardLayout`
  - 조각 = 다른 사각형·닫힌 선 조각 안에 들지 않은 rect/원 + 이어진 선 그룹. 선이 사각형 안인지는 `_lineInRect`(사각형 변 위에 겹친 선은 안이 아님 — 미드웨이를 상판 변에 붙여 그려도 선 조각 유지), 같은 자리 두 번 그린 선은 하나만. 돌린 rect는 회전 포함 상자 크기(`getBBox`)로, 그리기(`_expRectPathLocal`)도 회전 포함
  - 온장 배치 창: 오른쪽 클릭 = 90° 돌리기(`p.rotated`), Shift+오른쪽 클릭 = 선 조각만 각도 입력(그린 방향 0°, 반시계 +) → `item.rot`,
    저장 배치에 `rot` 기록(`_rotBox`로 상자 다시 계산해 복원)
  - 조각이 작아 안에 크기 글자가 안 들어가면 빈 곳에 글자 + 조각을 가리키는 화살표(`_boardPiece`, `tex.board`/`tex._used`):
    온장 안을 훑어 다른 조각·다른 바깥 글자와 안 겹치고 화살표가 다른 조각을 지나지 않는 자리, 없으면 캔버스 안(잘리지 않게).
    번호 칸도 안 들어가는 조각은 바깥 글자 앞에 번호 칸(`_pn`)을 붙임
  - 선 조각이 그대로 온장에 안 들어가면 변 하나를 가로로 눕힌 각도 중 들어가는(면적 최소) 것으로 돌림(`item.rot/rx0/ry0`, `_boardPiece`의 `M`이 적용)
  - 온장 배치 창(`renderBoardLayout`)은 제품 수와 상관없이 한 쪽에 2장씩(`goBoardPage` — 배치 그림(`#board-canvas-wrap`) 안쪽 좌우 가운데 큰 화살표 `.board-side-btn` #board-prev-btn/#board-next-btn, ← → 키, 머리줄엔 쪽 번호만). 제품별 행 배치는 그림으로 내보낼 때(targetCanvas)만
- 도면화(PDF): `exportDrawingA4` → `_drawCleanExport`(도면 쪽, `_exp*` 함수들) + `_renderCleanBoards`(온장 배치 쪽, 한 쪽에 최대 2장 `_BPP`, `bi0`로 "온장 N" 번호 유지)
  + 맨 끝 "사용 제품" 쪽 = 제품마다 한 쪽씩 온장 사진(`window._MALL_IMG[id]`, 불러오는 중이면 300ms마다 다시 넣음)·제품명·영문명·사이즈·장수 (공장 확인용)
  - 1쪽은 항상 **전체 도면**(모든 도형 원래 자리). 온장 2장 이상이면 2쪽부터 **온장마다 상세 한 쪽**("상세 · 온장 N"): `_drawingBoards`(저장 배치/자동 배치) → `_shapePieceMap`(도형 → 속한 조각: 조각 안·변 위 → 가장 작은 조각,
    밖이면 가장 가까운 조각, 그룹은 main 자리) → 쪽마다 `shapes`를 그 장 조각 것만으로 잠시 바꿔 `_renderDrawingImage`.
    이때 `_compactPageShapes`가 조각(+딸린 도형)을 원래 자리 대신 줄 맞춰 모은 복사본으로 바꿈(줄 폭을 바꿔 가며 도면 영역 `_DRW_AW×_DRW_AH`에 가장 크게, 간격 = 150px 상당 mm). 배치 안 된 조각은 따로 한 쪽.
    조각 번호는 `_autoPieceNums`를 `shapeNum`에 잠시 고정해 전체 기준 유지. 도면 쪽은 **항상 가로 A4**(`isPort=false`)
  - 밑면연마 띠는 50mm, 단 깊이가 더 큰 것(150×150 원클릭)은 그 깊이로·방향은 저장된 `inward`(가로선 +y, 세로선 +x)
  - 끌어 옮기는 치수 글자 공통: `dimLabels` 항목에 `start()/drag(ex,ey,dx,dy,st)` (선택·선 절단 도구 mousedown → `dimDragInfo`, document mousemove가 호출).
    지시선 글자 `s.lblOff[key]=[dx,dy]px`(`_lblOff/_lblDrag`, key: rc·r_코너·phi), 선 사이 각도 호 반지름 `line.angR{a|b}`(px),
    치수선 도구: 길이=offsetMm, 각도=x2,y2(반지름), R/Φ=끝점 회전. 모두 편집 화면 전용(도면화는 자동 자리)
  - 편집 화면 선 길이 치수(`drawDimsLine`)는 끌어서 옮김: `s.dimOffPx`(px, 바깥쪽 +, 자동 자리 8px 안이면 지움 → 자동). 도면화는 자동 자리 그대로
  - 도면화 조각 치수(사각 폭·높이, 선 조각의 가로·세로 선)는 `_expDimRows`(2026-10-27 사용자 확정 "공통 치수 빼고 치수 줄 쭉 맞추기"):
    같은 방향·같은 값·범위 50% 이상 겹침·조각 사이 800mm 이하인 것끼리 묶음(union-find, 이어진 조각 줄 전체) → 하나만.
    쪽(b→r→t→l)마다 바깥 변부터, 기존 줄 중 가장 가까운 줄에 붙임(보조선·치수선이 조각 안을 안 지나고 1500mm 이내, 같은 줄 범위 안 겹침), 없으면 자기 변 옆 새 줄(가까운 줄과 58px 간격).
    `_expDim(...,fixed)` = 치수선은 그 줄 그대로(글자만 자리 고름). 비스듬한 선·돌린 사각형·원은 예전처럼 그 자리
  - (편집 화면·DXF) 선 조각 가로/세로 선 치수는 `_lineDimPlan`으로 조각 상자 바깥 치수 줄(위·아래·왼·오)에 맞춤, 같은 쪽 범위가 겹치면 짧은 것부터 안쪽 줄
  - `_expDim`: 30px 미만 짧은 치수는 화살표를 바깥에서 안쪽으로, 글자는 화살표 너머
  - 범례는 가공이 없어도 항상: 실선 = 닫힘면, 주황 빗금 = 밑면연마(50mm), 검정 ▲ = 고스라, 빨간 ★ = 졸리컷
  - 겹침 방지: `_pdr`(글자 상자), `_pseg`(그린 선), `_pcut`(타공부 안쪽) 등록 후 `_expDim`/`_expBestDim`/`_expLeader`가 빈 자리 선택
- 3D 보기(`show3D`/`close3D`/`save3DImage`, WebGL 직접 구현 — 외부 라이브러리 없음): `_3dBuildScene`이 `_expCollect` 조각마다
  외곽·구멍 루프(`_3dLoops`: rect=`_expRectPath`, 선 조각=`_expChain`, 싱크볼/쿡탑·타공=구멍), 두께(`_3dThick`, 제품 사이즈 "12T", 없으면 12),
  윗면 텍스처 = 조각 모양으로 오린 온장 사진(`_drawingBoards` 배치 자리 → `_3dWorldToBoard`(= `_boardPiece`의 M) → 아핀 `_afMul/_afInv`로 `_drawSlab` 온장 캔버스를 옮겨 그림, 사진 없으면 돌 색).
  `_3dSetupGL`: 윗/밑면 = 조각 상자 사각형 + 텍스처(투명 버림, 삼각분할 없음), 옆면 = 루프 따라 세운 사각형(법선은 재료 바깥), 윗면 외곽선 = 이음선, 바닥판.
  하부장(기본 켬, 머리줄 "하부장" 체크 `_3d.furn` — 꺼도 상판은 900·세라믹 판은 그대로, 가구만 안 그림): 상판 윗면 900(`_3D_H`), 몸통 = 외곽을 20 들인 다각형(`_3dInset`) 벽, 걸레받이 100(+50 들임),
  민자 도어 = 앞면 변(`_3dFrontEdges`: 밑면연마·고스라 붙은 변, 없으면 도면 아래쪽을 보는 가장 긴 변)에 + 틈 선, 폭 300 미만 조각은 장 없음.
  나누기 `_3dDoorSplit(L,apps)`: 싱크볼·쿡탑 구멍(가장 가까운 앞면 변 하나에, `appAt`) 아래 = 폭+60을 100 단위 올림·가운데(800 이상 2짝), 겹치면 기기 사이 가운데, 150 미만 틈은 옆 장에, 나머지 약 500씩.
  싱크볼 구멍 아래 스테인리스 볼(깊이 200), 쿡탑 구멍에 검은 유리판(`fan`)
  상부장(머리줄 "상부장" 체크 `_3d.upper`, 하부장 체크와 무관, `_3dSetupGL` 5번째 인자): 미드웨이마다(`upSpans`, 바닥부터·판 제외) 그 벽 구간 위(미드웨이 윗변부터),
  미드웨이가 없으면 상판마다 가장 긴 `backs`(맞붙은 변 제외, 600 이상) 위 `_3D_UPGAP`(600). 깊이 `_3D_UPD` 350·높이 `_3D_UPH` 700, 도어 `_3dDoorSplit(L,[])`, 하부장 몸통·도어 배열에 같이(`furnDraw`)
  조각 구분(`_3dGetType/_3dSetType`, 도형 `piece3d` = top|obj|mid|front|side|etc(목록 이름 "삭제" = 3D에서만 안 그림), 선 조각은 선마다, 기본 = 폭 300 미만 etc·나머지 top,
  오브제 obj(2026-10-27, 선반·벤치 등 가구 아닌 상판) = 상판처럼 그리고 끌기·위아래(pos3d)도 같지만 하부장 없음·`backs`(미드웨이·상부장 자리) 아님,
  그 변(`ed.obj` = tops 항목)에 붙은 전면판·측판은 바닥부터가 아니라 오브제 밑면에 매달림(y = y0-Hm, 판의 mid3d.y0 무시) → tops 항목 `hang` = 매달린 판 높이,
  Shift 위아래의 바닥 맞춤 = 판이 바닥에 닿는 높이(`drag.vertTop.hang`), 3D 창 왼쪽 `_3dPiecePanel`, 머리글 누르면 접기 `_3dFold`/localStorage `scd_3d_fold`):
  미드웨이 = 상판 뒷변(`backs`: 앞면 아닌 300 이상 변, 긴 것부터)을 따라 상판 위에 세운 판(긴 변=벽 따라·짧은 변=높이·앞면 무늬), 기타 = 안 그림.
  머리줄 "상판만 / 상판+미드웨이"(`_3d.mode`, `_3dSetMode`).
  조각 구분 목록은 한 줄씩(번호·크기·종류 버튼 + 옮겼으면 ↺ = 그 조각 pos3d·mid3d·midFace 지움)만 — 자리·방향·높이·무늬 조절은 모두 3D 마우스(목록 조절 버튼은 없앰)
  미드웨이 자리 손으로: 도형(`_3dKey`) `mid3d={edge:'상판도형id:변번호', off:mm, swap}` (끌기로 정함, `scene.edges` = 모든 상판 변). 장면이 지금 자리를 `pc.mid`로 돌려줌.
  판 면에 붙이기(2026-10-27): 그린 판·미드웨이마다 평면 네 변을 `allEdges`에 `{id:'p도형id:i', pan:true, y:그 판 아랫변, n:판 바깥}`으로 넣음 → edge가 'p…'면 그 판 다음에 그림(`_3dPanelOrder`),
  자동 자리·`_3dMidContact`에는 안 씀. off는 변 밖으로 넘어도 됨(끝 min(20,len/2,Lm/2)만 걸치면). 끌기 자석 `_3dMagnet`(변 끝·상판 꼭짓점·다른 판 모서리 `midInfo.c`, 변에서 1500 안) + 기준선,
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
  하부장 전면판·측판: `piece3d` front|side(`_3dIsPanel`), 미드웨이 고리에서 같이 그림(상판만 보기에서도) — `_3dPanelEdge`(상판 변 그대로·y=0 → 바깥면 = 상판 끝, 두께만큼 안쪽), 높이 ≤ 상판 밑면(`ed.y0`, 하부장 끄면 안 그림).
  자동 = `_3dMidContact`, 없으면 전면판 = 앞면 변(`ed.front`, 긴 것부터) · 측판 = 앞면 아닌 1000 이하 변(짧은 것부터), 벽 변(`ed.wall` = 미드웨이가 붙은 변)·맞붙은 변(`ed.joint`)·이미 쓴 변(`usedP`) 제외, 변 가운데.
  판 높이 축 = 상판 밑면 높이에 가까운 치수. `pc.mid.panel`/`midInfo.panel` → 끌기 미리보기도 `_3dPanelEdge`(바닥 라인 판정 무시, 항상 바닥부터)
  상판 자리 손으로: 도형(`_3dKey`) `pos3d={dx,dz,rot,dy}`(rot = 조각 상자 가운데 기준 90°×n, dy = 900에서 위아래 mm — Shift+상판 끌기 `drag.vertTop`,
  0·바닥에 맞춤·바닥 밑 안 감, dy≠0이면 그 조각 하부장 안 그림 = 주방 상판이 아닌 선반·테이블 등), `_3dSetupGL`이 외곽·구멍·윗면 사각형·하부장에 적용, `R.tops[]={key,loops,y,pos}`.
  마우스(`show3D`): 왼쪽 = 조각 위면 선택(`_3d.sel`) + 끌기(`_3dPick` → 상판은 `_3dPlane` 평면 교점 차이 + `_3dSnap`(다른 상판 꼭짓점 x/z tol 안 맞춤) → `pos3d`, rAF로 `_3dRegeom`
  = 버퍼만 다시(텍스처·GL 프로그램은 `_3dGLC`에 캐시), 미드웨이는 미리보기 → 놓을 때 `mid3d`), 빈 곳 = 돌리기, 오른쪽/가운데/Shift 끌기 = 옮기기,
  기준선 `_3d.guide`(선 정점 배열, 끄는 동안만, mouseup에서 지움): `_3dSnap`이 맞춘 꼭짓점 쌍을 잇는 선(높이 다르면 세로로 이음), Shift 위아래는 900·바닥·다른 상판 윗면에 맞추고 `_3dHGuide`(그 높이 수평 테두리)
  → `_3dLabels`가 `#v3d-labels` 위 SVG 분홍 점선으로 그림(WebGL 선은 1px라 안 씀),
  오른쪽 클릭(안 움직임) = 상판 rot+1 / 미드웨이 swap, R 키 = 선택 조각 돌리기, 올림 `_3d.hover` 파랑·선택 주황 외곽선. "↺ 처음 배치로" = `_3dResetLayout`(pos3d·mid3d 지움)
  조각 번호표 `_3dLabels`(`_3dRender` 끝마다): `#v3d-labels`(캔버스 위 HTML, 이미지 저장엔 안 들어감)에 목록 번호(scene.pieces 순서) — 상판 윗면 안쪽 점·미드웨이/판 상자 가운데, 올림 파랑·선택 주황.
  목록 줄 `data-row` 올림 → `_3d.hover`, 번호·이름 `data-pick` 누르면 `_3d.sel`, 3D 올림·선택이면 목록 줄 배경 강조
  카메라 yaw/pitch/거리(`_3dSetView` iso/top/front), 좌표 X=도면 x·Z=도면 y·Y=위. 사진 불러오는 중이면 300ms마다 다시(`_3dRebuild`). PNG 저장은 `_pickSaveFile('img')`
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
  수전 → 가장 가까운 싱크볼 변(같은 줄 여러 개는 이어서 간격), 콘센트 등 → 가까운 선, Φ값은 치수 없는 쪽 지시선
- 레이어: `SC-PIECE` 조각 / `SC-CUTOUT` 싱크볼·쿡탑 / `SC-HOLE` 타공 / `SC-GRIND` 밑면연마 띠+45° 빗금 / `SC-GOSRA` 고스라 ▲
  / `SC-DIM` 치수(선+화살촉+글자) / `SC-NAME` 조각 이름 / `SC-NOTE` 도면 글자·화살표 / `SC-JOLLY` 졸리컷 ★ / `SC-TITLE` 표제란
- 다시 불러오기 호환: `SC-DIM/NOTE/GOSRA/JOLLY/TITLE`은 무시, `SC-GRIND` 띠는 해치처럼(밑면연마+고스라) 해석, 양식 블록(INSERT)은 무시

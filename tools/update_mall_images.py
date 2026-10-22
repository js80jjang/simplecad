# 윤현몰 제품 온장 이미지 → mall-img/<상품번호>.js
# mall-catalog.js의 img(목록 이미지 = 온장 전체 사진, 2:1)를 받아 작게 줄여 data URL로 저장.
# 앱은 이 파일을 <script>로 읽어서 온장 배치·도면화 2쪽에 무늬로 채움.
#   - 쇼핑몰 이미지 서버가 다른 사이트에서 쓰는 걸 허용하지 않아(CORS 없음) 바로 연결하면 도면화(PDF)가 막힘
#   - .js(data URL)로 두면 GitHub Pages·PC에서 바로 연 파일(file://) 모두에서 됨
# GitHub Actions(.github/workflows/mall-catalog.yml)가 제품 목록 갱신 뒤에 실행. 직접 실행: python tools/update_mall_images.py
# 필요: Pillow (pip install pillow)
import base64
import io
import json
import os
import re
import sys
import time
import urllib.request

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CATALOG = os.path.join(ROOT, 'mall-catalog.js')
OUT = os.path.join(ROOT, 'mall-img')
MANIFEST = os.path.join(OUT, 'manifest.json')  # {상품번호: 원본 주소|SPEC} — 같으면 다시 받지 않음 (SPEC가 바뀌면 전부 다시)
MAX_W = 1150     # 긴 쪽 픽셀. 쇼핑몰 온장 사진 원본이 1150×576이라 줄이지 않음 (파일 하나 ≈ 60KB)
QUALITY = 86
SPEC = 'w%d-q%d' % (MAX_W, QUALITY)
UA = 'Mozilla/5.0 (simplecad image updater; +https://github.com/js80jjang/simplecad)'


def load_catalog():
    txt = open(CATALOG, encoding='utf-8').read()
    m = re.search(r'window\._MALL_CATALOG=(\{.*\});', txt, re.S)
    return json.loads(m.group(1))['items']


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read()


def shrink(data):
    im = Image.open(io.BytesIO(data)).convert('RGB')
    im.thumbnail((MAX_W, MAX_W), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
    return buf.getvalue()


def main():
    os.makedirs(OUT, exist_ok=True)
    items = [it for it in load_catalog() if it.get('img') and it.get('id')]
    manifest = json.load(open(MANIFEST, encoding='utf-8')) if os.path.exists(MANIFEST) else {}
    keep, done, fail = set(), 0, 0
    for it in items:
        gid, src = str(it['id']), it['img']
        path = os.path.join(OUT, gid + '.js')
        keep.add(gid)
        if manifest.get(gid) == src + '|' + SPEC and os.path.exists(path):
            continue
        try:
            b64 = base64.b64encode(shrink(fetch(src))).decode('ascii')
        except Exception as e:  # 하나 실패해도 나머지는 계속
            print('실패', gid, e, file=sys.stderr)
            fail += 1
            continue
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write('// 자동 생성 — tools/update_mall_images.py\n'
                    'window._MALL_IMG=window._MALL_IMG||{};window._MALL_IMG["%s"]="data:image/jpeg;base64,%s";\n' % (gid, b64))
        manifest[gid] = src + '|' + SPEC
        done += 1
        time.sleep(0.3)  # 쇼핑몰에 부담 주지 않게
    # 목록에서 빠진 제품 이미지는 지움
    for fn in os.listdir(OUT):
        gid = fn[:-3] if fn.endswith('.js') else None
        if gid and gid not in keep:
            os.remove(os.path.join(OUT, fn))
            manifest.pop(gid, None)
    manifest = {k: manifest[k] for k in sorted(manifest) if k in keep}
    with open(MANIFEST, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=0)
    print('이미지 새로 받음 %d개, 실패 %d개, 전체 %d개' % (done, fail, len(manifest)))


if __name__ == '__main__':
    main()

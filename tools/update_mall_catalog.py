# 윤현몰(younhyunmall.com) 상품 목록 → mall-catalog.js
# GitHub Actions(.github/workflows/mall-catalog.yml)가 매일 실행하고, 바뀌었으면 커밋함.
# 심플캐드의 제품명 검색이 이 목록을 씀 (브라우저는 쇼핑몰을 직접 못 읽어서 미리 만들어 둠).
# 표준 라이브러리만 사용. 직접 실행: python tools/update_mall_catalog.py
import datetime
import html
import json
import os
import re
import sys
import time
import urllib.request

BASE = 'https://www.younhyunmall.com/goods/goods_list.php'
# 가져올 분류 (cateCd). 세라믹 빅슬랩 009001 = 두께 6mm, 009003 = 두께 12mm (009004 = 6mm+12mm 묶음). 다른 분류는 여기에 추가
CATEGORIES = ['009003', '009001']
PAGE_SIZE = 100
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mall-catalog.js')
UA = 'Mozilla/5.0 (simplecad catalog updater; +https://github.com/js80jjang/simplecad)'

SIZE_RE = re.compile(r'(\d{3,4})\s*[xX×*]\s*(\d{3,4})\s*[xX×*]\s*(\d+(?:\.\d+)?)\s*(?:\(\s*t\s*\))?\s*mm', re.I)


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode('utf-8', 'replace')


def text(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()


def money(s):
    d = re.sub(r'[^\d]', '', text(s))
    return int(d) if d else None


def parse(page):
    items = []
    # 상품 하나 = <div class="item_cont"> … <!-- //item_cont -->
    for block in re.findall(r'<div class="item_cont">(.*?)<!-- //item_cont -->', page, re.S):
        gid = re.search(r'goodsNo=(\d+)', block)
        en = re.search(r'<strong class="item_name">(.*?)</strong>', block, re.S)
        ex = re.search(r'<span class="item_name_explain">(.*?)</span>', block, re.S)
        if not gid or not en:
            continue
        explain = text(ex.group(1)) if ex else ''
        m = SIZE_RE.search(explain)
        size = '%s×%s×%sT' % (m.group(1), m.group(2), m.group(3)) if m else ''
        ko = text(SIZE_RE.sub('', explain)) if explain else ''
        price = re.search(r'<strong class="item_price">.*?<span[^>]*>(.*?)</span>', block, re.S)
        m2 = re.search(r'<div class="m2"><span>(.*?)</span>', block, re.S)
        img = re.search(r'data-image-list\s*=\s*"([^"]+)"', block) or re.search(r'<img\s+src="([^"]+)"', block)
        items.append({
            'id': gid.group(1),
            'name': ko or text(en.group(1)),   # 도면·견적에 쓰는 이름 (한글)
            'en': text(en.group(1)),          # 검색용 영문 이름
            'size': size,                     # 예: 1600×3200×12T
            'price': money(price.group(1)) if price else None,   # 장당
            'm2': money(m2.group(1)) if m2 else None,            # ㎡당
            'img': img.group(1) if img else '',
            'url': 'https://www.younhyunmall.com/goods/goods_view.php?goodsNo=' + gid.group(1),
        })
    return items


def main():
    seen, all_items = set(), []
    for cate in CATEGORIES:
        for page_no in range(1, 30):
            url = '%s?cateCd=%s&pageNum=%d&page=%d' % (BASE, cate, PAGE_SIZE, page_no)
            items = [it for it in parse(fetch(url)) if it['id'] not in seen]
            if not items:
                break
            for it in items:
                it['cate'] = cate
                seen.add(it['id'])
            all_items.extend(items)
            time.sleep(1)  # 쇼핑몰에 부담 주지 않게
    # 너무 적으면(쇼핑몰 화면이 바뀌었거나 접속 실패) 기존 목록을 지우지 않고 실패로 끝냄
    if len(all_items) < 10:
        print('상품을 %d개밖에 못 읽었습니다. 기존 mall-catalog.js 유지.' % len(all_items), file=sys.stderr)
        sys.exit(1)
    data = {
        'updated': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y-%m-%d'),
        'source': 'https://www.younhyunmall.com',
        'items': all_items,
    }
    body = json.dumps(data, ensure_ascii=False, indent=0, separators=(',', ':'))
    js = ('// 자동 생성 파일 — tools/update_mall_catalog.py (GitHub Actions 매일 실행). 직접 고치지 마세요.\n'
          'window._MALL_CATALOG=' + body + ';\n')
    # 날짜만 바뀐 경우엔 파일을 그대로 둠 (쓸데없는 커밋 방지)
    if os.path.exists(OUT):
        old = open(OUT, encoding='utf-8').read()
        strip = lambda s: re.sub(r'"updated":"[^"]*"', '', s)
        if strip(old) == strip(js):
            print('변경 없음 (%d개)' % len(all_items))
            return
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    print('mall-catalog.js 저장: %d개' % len(all_items))


if __name__ == '__main__':
    main()

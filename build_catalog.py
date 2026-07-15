"""
세라믹제품목록.xlsx → 제품목록.js 생성 스크립트
세라믹_가공비_계산.bat 실행 시 자동으로 호출됩니다.
"""
import os, json, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
XLSX_FILE = os.path.join(BASE_DIR, "세라믹제품목록.xlsx")
OUT_FILE  = os.path.join(BASE_DIR, "제품목록.js")

def parse_excel(path):
    try:
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.active
        rows = [tuple(c.value for c in row) for row in ws.iter_rows()]
        wb.close()
        return rows
    except ImportError:
        pass
    try:
        import xlrd
        wb = xlrd.open_workbook(path)
        ws = wb.sheet_by_index(0)
        return [tuple(ws.cell_value(r, c) for c in range(ws.ncols)) for r in range(ws.nrows)]
    except ImportError:
        pass
    import pandas as pd
    df = pd.read_excel(path, header=None, dtype=str).fillna('')
    return [tuple(row) for row in df.values.tolist()]

def find_name_size_cols(header_row):
    """헤더 행에서 제품명/사이즈 열 인덱스 탐지"""
    name_col, size_col = 1, 2  # 기본값
    for ci, cell in enumerate(header_row):
        val = str(cell or '').strip()
        if any(k in val for k in ('제품명', '품명', '제품', 'Name', 'name')):
            name_col = ci
        if any(k in val for k in ('사이즈', '규격', '크기', 'Size', 'size')):
            size_col = ci
    return name_col, size_col

def build_catalog(rows):
    if not rows:
        return []
    # 헤더 행 탐지 (첫 5행 중 제품명/사이즈 키워드 있는 행)
    header_row_idx = 0
    for ri, row in enumerate(rows[:5]):
        joined = ' '.join(str(c or '') for c in row)
        if any(k in joined for k in ('제품명', '품명', '사이즈', '규격')):
            header_row_idx = ri
            break
    name_col, size_col = find_name_size_cols(rows[header_row_idx])
    catalog = []
    for row in rows[header_row_idx + 1:]:
        name = str(row[name_col] if name_col < len(row) else '').strip()
        size = str(row[size_col] if size_col < len(row) else '').strip()
        # 빈 행, 숫자만 있는 행 제외
        if not name or name in ('None', '') or name.replace('.','').replace(',','').isdigit():
            continue
        # nan 제거
        if name.lower() == 'nan':
            continue
        catalog.append({'name': name, 'size': size})
    return catalog

def main():
    if not os.path.exists(XLSX_FILE):
        print(f"[build_catalog] 엑셀 파일 없음: {XLSX_FILE}")
        with open(OUT_FILE, 'w', encoding='utf-8') as f:
            f.write('window._PRODUCT_CATALOG=[];\n')
        return
    try:
        rows = parse_excel(XLSX_FILE)
        catalog = build_catalog(rows)
        js = 'window._PRODUCT_CATALOG=' + json.dumps(catalog, ensure_ascii=False) + ';\n'
        with open(OUT_FILE, 'w', encoding='utf-8') as f:
            f.write(js)
        print(f"[build_catalog] 제품 {len(catalog)}개 → 제품목록.js 생성 완료")
    except Exception as e:
        print(f"[build_catalog] 오류: {e}")
        import traceback; traceback.print_exc()
        with open(OUT_FILE, 'w', encoding='utf-8') as f:
            f.write('window._PRODUCT_CATALOG=[];\n')

if __name__ == '__main__':
    main()

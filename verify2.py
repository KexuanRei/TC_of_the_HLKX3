# -*- coding: utf-8 -*-
import zipfile, sys, io, re
from lxml import etree
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DST = r'C:\Users\Kexuan\Documents\deepseek-harness\default-workspace\船号_离线测试版_依赖表超链接.xlsx'
M = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
R = '{http://schemas.openxmlformats.org/package/2006/relationships}'
with zipfile.ZipFile(DST) as z:
    s7 = etree.fromstring(z.read('xl/worksheets/sheet7.xml'))
    print('== sheet7 单元格 ==')
    for row in s7.findall(f'{M}sheetData/{M}row'):
        for c in row.findall(f'{M}c'):
            v = ''.join(t.text or '' for t in c.iter(f'{M}t'))
            print(f'  {c.get("r")}: {v}')
    rels = etree.fromstring(z.read('xl/worksheets/_rels/sheet7.xml.rels'))
    tmap = {rel.get('Id'): rel.get('Target') for rel in rels.findall(f'{R}Relationship')}
    print('== sheet7 超链接 (ref -> target) ==')
    for h in s7.findall(f'{M}hyperlinks/{M}hyperlink'):
        print(f'  {h.get("ref")} -> {tmap.get(h.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"))}')
    app = z.read('docProps/app.xml').decode('utf-8')
    print('\n== app.xml 片段 ==')
    i = app.find('TitlesOfParts')
    print(app[max(0,i-60):i+400])

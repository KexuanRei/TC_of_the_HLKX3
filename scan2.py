# -*- coding: utf-8 -*-
import zipfile, sys, io, re
from lxml import etree

out = io.StringIO()
def w(*a):
    print(*a, file=out)

path = r'D:\CH\船号_离线测试版.xlsx'
keys = ['舾装辅助列','计划表','材料准备','六百六十六','转涂','数据更新','数据中继','重点监控','依赖','kdocs','金山','WPS','链接']
z = zipfile.ZipFile(path)
names = z.namelist()
w('== xml/rels parts ==')
for n in names:
    if (n.endswith('.xml') or n.endswith('.rels')) and 'worksheet' not in n and 'sharedStrings' not in n:
        w(' ', n)

nsm = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
M = f'{{{nsm}}}'

# external links: file names
w('\n== externalLinks contents (external workbook names) ==')
for n in names:
    if n.startswith('xl/externalLinks/') and n.endswith('.xml'):
        root = etree.fromstring(z.read(n))
        for el in root.iter(f'{M}externalBook'):
            rid = el.get(f'{{http://schemas.openxmlformats.org/officeDocument/2006/relationships}}id')
            w(f'  {n}: r:id={rid}')
    if n == 'xl/externalLinks/_rels/externalLink1.xml.rels':
        pass
for n in names:
    if n.startswith('xl/externalLinks/_rels/') and n.endswith('.rels'):
        w(f'  {n}:')
        w('   ' + z.read(n).decode('utf-8','ignore').replace('><', '>\n   <'))

# shared strings
shared = []
if 'xl/sharedStrings.xml' in names:
    root = etree.fromstring(z.read('xl/sharedStrings.xml'))
    for si in root.findall(f'{M}si'):
        shared.append(''.join(t.text or '' for t in si.iter(f'{M}t')))
w(f'\nshared strings: {len(shared)}')
w('== shared strings containing keywords ==')
for i, s in enumerate(shared):
    for k in keys:
        if k in s:
            w(f'  [{i}] {s[:150]}')
            break

# cells with keyword values
w('\n== cells whose value contains a keyword ==')
sheet_names = {}
wbroot = etree.fromstring(z.read('xl/workbook.xml'))
for sh in wbroot.findall(f'{M}sheets/{M}sheet'):
    sheet_names[sh.get(f'{{http://schemas.openxmlformats.org/officeDocument/2006/relationships}}id')] = sh.get('name')
wb_rels = etree.fromstring(z.read('xl/_rels/workbook.xml.rels'))
R = '{http://schemas.openxmlformats.org/package/2006/relationships}'
rel_map = {}
for rel in wb_rels.findall(f'{R}Relationship'):
    rel_map[rel.get('Id')] = rel.get('Target')
title_of = {}
for part in names:
    m = re.match(r'xl/worksheets/(sheet\d+)\.xml$', part)
    if not m:
        continue
    sheet = m.group(1)
    title = None
    for rid, target in rel_map.items():
        if target == f'worksheets/{sheet}.xml':
            title = sheet_names.get(rid)
    if title is None:
        title = sheet
    title_of[sheet] = title
    root = etree.fromstring(z.read(part))
    for c in root.iter(f'{M}c'):
        t = c.get('t')
        if t == 's':
            v = c.find(f'{M}v')
            if v is None or v.text is None: continue
            try: val = shared[int(v.text)]
            except Exception: continue
        elif t == 'inlineStr':
            val = ''.join(x.text or '' for x in c.iter(f'{M}t'))
        elif t == 'str':
            v = c.find(f'{M}v')
            val = (v.text or '') if v is not None else ''
        else:
            continue
        for k in keys:
            if k in val:
                w(f'  [{title}]!{c.get("r")}: {val[:120]}')
                break

# hyperlinks per sheet
w('\n== hyperlinks per sheet (cell -> target) ==')
for n in names:
    m = re.match(r'xl/worksheets/(sheet\d+)\.xml$', n)
    if not m: continue
    sheet = m.group(1)
    root = etree.fromstring(z.read(n))
    cells = {}
    for c in root.iter(f'{M}c'):
        h = c.find(f'{M}hyperlinks' if False else f'{M}hyperlinks')
    # simpler: iterate hyperlinks elements
    hrefs = {}
    for h in root.iter(f'{M}hyperlink'):
        ref = h.get('ref')
        rid = h.get(f'{{http://schemas.openxmlformats.org/officeDocument/2006/relationships}}id')
        hrefs[ref] = rid
    rels_part = f'xl/worksheets/_rels/{sheet}.xml.rels'
    if hrefs and rels_part in names:
        rr = etree.fromstring(z.read(rels_part))
        tmap = {rel.get('Id'): rel.get('Target') for rel in rr.findall(f'{R}Relationship')}
        title = title_of.get(sheet, sheet)
        w(f'  [{title}] ({len(hrefs)} links)')
        for ref, rid in hrefs.items():
            w(f'    {ref}: {tmap.get(rid)}')

data = out.getvalue()
with open(r'C:\Users\Kexuan\Documents\deepseek-harness\default-workspace\scan_result.txt','w',encoding='utf-8') as f:
    f.write(data)
print('done, length', len(data))

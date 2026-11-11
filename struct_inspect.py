# -*- coding: utf-8 -*-
import zipfile, sys, io, re
from lxml import etree
out = io.StringIO()
def w(*a): print(*a, file=out)

path = r'D:\CH\船号_离线测试版.xlsx'
z = zipfile.ZipFile(path)
names = z.namelist()
w('worksheets parts:', [n for n in names if re.match(r'xl/worksheets/sheet\d+\.xml$', n)])
w('worksheet rels parts:', [n for n in names if re.match(r'xl/worksheets/_rels/', n)])
w()
w('== [Content_Types].xml ==')
w(z.read('[Content_Types].xml').decode('utf-8'))
w()
w('== xl/workbook.xml ==')
w(z.read('xl/workbook.xml').decode('utf-8'))
w()
w('== xl/_rels/workbook.xml.rels ==')
w(z.read('xl/_rels/workbook.xml.rels').decode('utf-8'))
w()
# hyperlink element structure in sheet2
root = etree.fromstring(z.read('xl/worksheets/sheet2.xml'))
M = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
hl = root.find(f'{M}hyperlinks')
w('== sheet2 hyperlinks element (first 3) ==')
if hl is not None:
    for h in hl[:3]:
        w(etree.tostring(h, encoding='unicode'))
# one inlineStr example anywhere? and one hyperlinked cell c element
w('== example hyperlinked <c> in sheet2 ==')
for c in root.iter(f'{M}c'):
    h = c.find(f'{M}hyperlink')
    if h is not None:
        w(etree.tostring(c, encoding='unicode')[:800])
        break
w()
w('== styles.xml cellXfs (first 8) ==')
st = etree.fromstring(z.read('xl/styles.xml'))
xfs = st.find(f'{M}cellXfs')
for xf in xfs[:8]:
    w(etree.tostring(xf, encoding='unicode'))

with open(r'C:\Users\Kexuan\Documents\deepseek-harness\default-workspace\struct.txt','w',encoding='utf-8') as f:
    f.write(out.getvalue())
print('ok')

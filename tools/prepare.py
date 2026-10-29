"""الخطوة 0: فك الأرشيف المحلي Nuketown for GTA V.zip واستخراج الحزم المتداخلة من dlc.rpf إلى ./ex
الاستخدام: python tools/prepare.py "Nuketown for GTA V.zip"
"""
import os, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpf_ex import extract
zp = sys.argv[1]
os.makedirs('ex', exist_ok=True)
z = zipfile.ZipFile(zp)
name = [n for n in z.namelist() if n.endswith('dlc.rpf')][0]
buf = z.read(name)
enc, res = extract(buf, 0, None)
for p, k, a, d in res:
    if p.endswith('.rpf'):
        open('ex/' + os.path.basename(p), 'wb').write(d); print('extracted', p, len(d))

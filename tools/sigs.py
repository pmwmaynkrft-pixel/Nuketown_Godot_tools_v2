"""بصمة الهندسة لكل نموذج (لاكتشاف النماذج المتطابقة هندسيًا) -> proj/maps/nuketown/_meta/geom_sig.json"""
import os, sys, json, hashlib, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from ydr import *; from joaat import joaat
files = load_rpf('ex/nuketown.rpf'); E = pickle.load(open('out/entities.pkl', 'rb'))
byhash = {joaat(n.rsplit('.', 1)[0]): n for n in files}
used = sorted({byhash[e['arch']] for e in E}); sig = {}
for n in used:
    v = files[n]; raw, fl = (v if isinstance(v, tuple) else (v, None)); dr = parse_ydr(raw, fl, frag=n.endswith('.yft'))
    h = hashlib.md5()
    for g in dr.models[0]:
        h.update(np.ascontiguousarray(g['pos']).tobytes()); h.update(g['idx'].tobytes())
        if g['uv'] is not None: h.update(np.ascontiguousarray(g['uv']).tobytes())
        sh = dr.shaders[g['shader']]; h.update(str(sorted(sh['tex'].items())).encode() + bytes([sh['bucket']]))
    sig[n.rsplit('.', 1)[0]] = h.hexdigest()[:12]
os.makedirs(os.getcwd() + '/proj/maps/nuketown/_meta', exist_ok=True)
json.dump(sig, open(os.getcwd() + '/proj/maps/nuketown/_meta/geom_sig.json', 'w'))
print('sigs', len(sig), 'unique', len(set(sig.values())))

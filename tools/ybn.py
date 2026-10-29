import os
import struct, sys, collections
import numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from rsc import *
def P(x): return x&0x0FFFFFFF
def parse_geom(d,o):
    typ=d[o+0x10]
    quant=np.array(struct.unpack_from('<3f',d,o+0x90),np.float32); cen=np.array(struct.unpack_from('<3f',d,o+0xA0),np.float32)
    vp=P(struct.unpack_from('<Q',d,o+0x78)[0]); pp=P(struct.unpack_from('<Q',d,o+0x88)[0])
    pc=struct.unpack_from('<I',d,o+0x84)[0]; vc=struct.unpack_from('<I',d,o+0xD4)[0]
    tris=[]; other=collections.Counter()
    for i in range(pc):
        q=pp+i*16; t=d[q]&7
        if t==0:
            tris.append(struct.unpack_from('<3H',d,q+4))
        else: other[t]+=1
    tr=np.array(tris,np.int64).reshape(-1,3)
    n=int(tr.max())+1 if len(tr) else 0
    vs=np.frombuffer(d,dtype='<i2',count=n*3,offset=vp).reshape(-1,3).astype(np.float32)*quant+cen
    return typ,vs,tr,other
def parse_ybn(raw,fl=None):
    r=Res(raw,fl); d=r.data
    typ=d[0x10]; res=[]; other=collections.Counter(); kinds=collections.Counter()
    def child(o):
        t=d[o+0x10]; kinds[t]+=1
        if t in (4,8):
            _,vs,tr,oth=parse_geom(d,o); other.update(oth)
            if len(tr): res.append((vs,tr))
    if typ==10:
        arr=P(struct.unpack_from('<Q',d,0x70)[0]); cnt=struct.unpack_from('<H',d,0xA0)[0]
        for i in range(cnt):
            p=struct.unpack_from('<Q',d,arr+i*8)[0]
            if p: child(P(p))
    else: child(0)
    return res,other,kinds
if __name__=='__main__':
    cols=load_rpf('ex/nuketown_cols.rpf')
    ok=0; bad=[]; nv=0; nt=0; oth=collections.Counter(); kinds=collections.Counter(); allm=[]
    for n,v in sorted(cols.items()):
        raw,fl=(v if isinstance(v,tuple) else (v,None))
        try:
            res,o,k=parse_ybn(raw,fl); ok+=1; oth.update(o); kinds.update(k)
            for vs,tr in res: nv+=len(vs); nt+=len(tr); allm.append((n,vs,tr))
        except Exception as e: bad.append((n,repr(e)[:80]))
    print('ok',ok,'bad',len(bad),bad[:3]); print('verts',nv,'tris',nt,'non-tri polys',dict(oth),'child kinds',dict(kinds))
    import pickle; pickle.dump(allm,open('out/cols.pkl','wb'))
    V=np.concatenate([a[1] for a in allm]); print(V.min(0),V.max(0))

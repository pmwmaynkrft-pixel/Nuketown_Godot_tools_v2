import os
import struct, sys
import numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from rsc import *
from joaat import joaat
TYPE_SIZE={1:4,2:4,3:8,4:4,5:8,6:12,7:16,8:4,9:4,10:4,11:4}
H_DIFF=joaat('diffusesampler'); H_TEXS=joaat('texturesampler'); H_BUMP=joaat('bumpsampler')
def cstr(d,o):
    e=d.index(b'\0',o); return d[o:e].decode('latin1')
def P(ptr): return ptr&0x0FFFFFFF
def decode_comp(t,raw):
    if t==6: return np.frombuffer(raw,dtype='<f4').reshape(-1,3)
    if t==5: return np.frombuffer(raw,dtype='<f4').reshape(-1,2)
    if t==7: return np.frombuffer(raw,dtype='<f4').reshape(-1,4)
    if t==1: return np.frombuffer(raw,dtype='<f2').astype(np.float32).reshape(-1,2)
    if t==3: return np.frombuffer(raw,dtype='<f2').astype(np.float32).reshape(-1,4)
    if t==8:
        v=np.frombuffer(raw,dtype='<u4')
        def s(x,b): 
            x=x.astype(np.int32); x=np.where(x>=(1<<(b-1)),x-(1<<b),x); return x/float((1<<(b-1))-1)
        return np.stack([s(v&1023,10),s((v>>10)&1023,10),s((v>>20)&1023,10)],1).astype(np.float32)
    if t in(9,10,11): return np.frombuffer(raw,dtype='u1').reshape(-1,4)
    raise ValueError('type %d'%t)
class Drawable: pass
def parse_ydr(raw, flags=None, frag=False):
    r=Res(raw,flags); d=r.data
    B=P(struct.unpack_from('<Q',d,0x30)[0]) if frag else 0
    dr=Drawable(); dr.shaders=[]; dr.models=[]
    # bounds
    dr.bbmin=struct.unpack_from('<3f',d,B+0x30); dr.bbmax=struct.unpack_from('<3f',d,B+0x40)
    sg=struct.unpack_from('<Q',d,B+0x10)[0]
    if sg:
        o=P(sg); sp=struct.unpack_from('<Q',d,o+0x10)[0]; sc=struct.unpack_from('<H',d,o+0x18)[0]
        for i in range(sc):
            so=P(struct.unpack_from('<Q',d,P(sp)+i*8)[0])
            pp=struct.unpack_from('<Q',d,so)[0]; shash=struct.unpack_from('<I',d,so+8)[0]
            cnt=d[so+0x10]; bucket=d[so+0x11]; psize=struct.unpack_from('<H',d,so+0x14)[0]
            fh=struct.unpack_from('<I',d,so+0x18)[0]
            tex={}
            vec={}
            for k in range(cnt):
                typ=d[P(pp)+k*16]; ptr=struct.unpack_from('<Q',d,P(pp)+k*16+8)[0]
                h=struct.unpack_from('<I',d,P(pp)+psize+k*4)[0]
                if typ==0 and ptr:
                    to=P(ptr); nm=struct.unpack_from('<Q',d,to+0x28)[0]
                    tex[h]=cstr(d,P(nm)) if nm else None
            dr.shaders.append(dict(hash=shash,file=fh,bucket=bucket,tex=tex))
    hp=struct.unpack_from('<Q',d,B+0x50)[0]
    if hp:
        lo=P(hp); ap=struct.unpack_from('<Q',d,lo)[0]; n=struct.unpack_from('<H',d,lo+8)[0]
        for i in range(n):
            mo=P(struct.unpack_from('<Q',d,P(ap)+i*8)[0])
            gp=struct.unpack_from('<Q',d,mo+8)[0]; gc=struct.unpack_from('<H',d,mo+0x10)[0]
            smp=struct.unpack_from('<Q',d,mo+0x20)[0]
            geoms=[]
            for g in range(gc):
                go=P(struct.unpack_from('<Q',d,P(gp)+g*8)[0])
                vb=P(struct.unpack_from('<Q',d,go+0x18)[0]); ib=P(struct.unpack_from('<Q',d,go+0x38)[0])
                icount=struct.unpack_from('<I',d,go+0x58)[0]; vcount=struct.unpack_from('<H',d,go+0x60)[0]
                stride=struct.unpack_from('<H',d,vb+8)[0]
                vptr=struct.unpack_from('<Q',d,vb+0x10)[0]; vc2=struct.unpack_from('<I',d,vb+0x18)[0]
                decl=P(struct.unpack_from('<Q',d,vb+0x30)[0])
                flags_=struct.unpack_from('<I',d,decl)[0]; dstride=struct.unpack_from('<H',d,decl+4)[0]
                types=struct.unpack_from('<Q',d,decl+8)[0]
                assert dstride==stride,(dstride,stride)
                b,x=r.at(vptr); vdata=b[x:x+vc2*stride]
                arr=np.frombuffer(vdata,dtype='u1').reshape(vc2,stride)
                comps={}; off=0
                for c in range(16):
                    if flags_>>c&1:
                        t=(types>>(4*c))&0xF; sz=TYPE_SIZE[t]
                        comps[c]=(t,off,sz); off+=sz
                assert off==stride,(off,stride,hex(flags_),hex(types))
                def get(c):
                    t,o,sz=comps[c]; return decode_comp(t,np.ascontiguousarray(arr[:,o:o+sz]).tobytes())
                pos=get(0)
                nrm=get(3) if 3 in comps else None
                uv=get(6)[:,:2] if 6 in comps else None
                col=get(4) if 4 in comps else None
                ibc=struct.unpack_from('<I',d,ib+8)[0]; iptr=struct.unpack_from('<Q',d,ib+0x10)[0]
                b2,x2=r.at(iptr); idx=np.frombuffer(b2[x2:x2+ibc*2],dtype='<u2').astype(np.uint32)
                sidx=struct.unpack_from('<H',d,P(smp)+g*2)[0] if smp else 0
                geoms.append(dict(pos=pos,nrm=nrm,uv=uv,col=col,idx=idx,shader=sidx,flags=flags_))
            dr.models.append(geoms)
    return dr
if __name__=='__main__':
    import collections,traceback
    files=load_rpf('ex/nuketown.rpf')
    ok=0; bad=[]; tv=0; tt=0
    for n,v in sorted(files.items()):
        if not n.endswith('.ydr'): continue
        raw,fl=(v if isinstance(v,tuple) else (v,None))
        try:
            dr=parse_ydr(raw,fl); ok+=1
            for m in dr.models:
                for g in m: tv+=len(g['pos']); tt+=len(g['idx'])//3
        except Exception as e:
            bad.append((n,repr(e)[:80]))
    print('ok',ok,'bad',len(bad),'verts',tv,'tris',tt)
    c=collections.Counter(b[1] for b in bad); print(c.most_common(8)); print(bad[:5])

import os
import struct, sys, collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from rsc import *
def parse_ymap(raw,fl=None):
    r=Res(raw,fl); d=r.data
    bp=P(struct.unpack_from('<Q',d,0x30)[0]); bc=struct.unpack_from('<H',d,0x4C)[0]
    blocks=[]
    for i in range(bc):
        h,ln,ptr=struct.unpack_from('<IIQ',d,bp+i*16); blocks.append((h,ln,P(ptr)))
    return d,blocks
def P(x): return x&0x0FFFFFFF
def entities(d,blocks):
    out=[]
    for h,ln,o in blocks:
        if h!=0xce501483: continue
        for k in range(ln//0x80):
            e=o+k*0x80
            arch,flags,guid=struct.unpack_from('<III',d,e+8)
            pos=struct.unpack_from('<3f',d,e+0x20); q=struct.unpack_from('<4f',d,e+0x30)
            sxy,sz,parent=struct.unpack_from('<ffi',d,e+0x40)
            lod,clod,lvl,nch,prio=struct.unpack_from('<ffIII',d,e+0x4C)
            out.append(dict(arch=arch,flags=flags,guid=guid,pos=pos,q=q,sxy=sxy,sz=sz,parent=parent,lod=lod,clod=clod,lvl=lvl,nch=nch))
    return out
if __name__=='__main__':
    from joaat import joaat
    md=load_rpf('ex/nuketown_metadata.rpf'); mdl=load_rpf('ex/nuketown.rpf')
    names={joaat(n.rsplit('.',1)[0]):n for n in mdl}
    tot=0; unres=collections.Counter(); res=0; blockhashes=collections.Counter(); lvls=collections.Counter()
    ents_all=[]
    for n,v in sorted(md.items()):
        if not n.endswith('.ymap'): continue
        raw,fl=(v if isinstance(v,tuple) else (v,None))
        d,blocks=parse_ymap(raw,fl)
        for h,ln,o in blocks: blockhashes[hex(h)]+=ln
        es=entities(d,blocks)
        for e in es:
            e['ymap']=n; ents_all.append(e)
            if e['arch'] in names: res+=1
            else: unres[e['arch']]+=1
            lvls[e['lvl']]+=1
        print(n,len(es),'blocks',[hex(b[0]) for b in blocks if b[0]!=0xce501483][:6])
    print('entities',len(ents_all),'resolved',res,'unresolved',sum(unres.values()),'distinct unresolved',len(unres))
    print('lod levels',lvls)
    print('blockhashes',dict(blockhashes))
    import pickle; pickle.dump(ents_all,open('out/entities.pkl','wb'))

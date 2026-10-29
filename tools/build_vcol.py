import sys, os, re, pickle, numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from ydr import *; from gltfw import *; from joaat import joaat
MAP=os.getcwd()+'/proj/maps/nuketown'; OFF=np.array([6000.0,10000.0,0.0])
files=load_rpf('ex/nuketown.rpf'); E=pickle.load(open('out/entities.pkl','rb')); S=pickle.load(open('out/model_stats.pkl','rb'))
byhash={joaat(n.rsplit('.',1)[0]):n for n in files}
def qmat(q):
    x,y,z,w=q
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
cache={}; gw=GW(); mat=gw.material('collision',None); roots=[]; tot=0
for k,e in enumerate(E):
    n=byhash[e['arch']]; st=S[n]
    if not n.endswith('.ydr') or 'mountain' in n or 'foliage' in n or st['ext']<4: continue
    if n not in cache:
        v=files[n]; raw,fl=(v if isinstance(v,tuple) else (v,None)); dr=parse_ydr(raw,fl)
        P_=[];I_=[];o=0
        for g in dr.models[0]:
            idx=g['idx'].reshape(-1,3); P_.append(g['pos']); I_.append(idx+o); o+=len(g['pos'])
        cache[n]=(np.concatenate(P_),np.concatenate(I_))
    pts,idx=cache[n]
    q=e['q']; q=(-q[0],-q[1],-q[2],q[3]); R=qmat(q)
    w=(pts*np.array([e['sxy'],e['sxy'],e['sz']]))@R.T+np.array(e['pos'])-OFF
    # drop degenerate tris
    ok=(idx[:,0]!=idx[:,1])&(idx[:,1]!=idx[:,2])&(idx[:,0]!=idx[:,2]); idx=idx[ok]
    both=np.concatenate([idx,idx[:,::-1]]); tot+=len(idx)
    nm='%s_%d'%(re.sub(r'^nkt_','',n[:-4])[:40],k)
    mi=gw.mesh(nm,[dict(pos=w.astype(np.float32),idx=both.reshape(-1).astype(np.uint32),mat=mat)])
    roots.append(gw.node(nm+'-colonly',mesh=mi))
gw.save(MAP+'/collision/nuketown_structures_collision.gltf',roots)
print('structure collision nodes',len(roots),'tris',tot)

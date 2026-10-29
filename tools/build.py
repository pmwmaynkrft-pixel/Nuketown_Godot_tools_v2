import sys, os, re, pickle, json, shutil, collections, math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from ydr import *; from gltfw import *; from joaat import joaat
PROJ=os.getcwd()+'/proj'; MAP=PROJ+'/maps/nuketown'
os.makedirs(MAP+'/models',exist_ok=True); os.makedirs(MAP+'/textures',exist_ok=True)
files=load_rpf('ex/nuketown.rpf'); E=pickle.load(open('out/entities.pkl','rb'))
byhash={joaat(n.rsplit('.',1)[0]):n for n in files}
used=sorted({byhash[e['arch']] for e in E})
print('archetypes used',len(used),'of',sum(1 for n in files if n.endswith(('.ydr','.yft'))))
texidx=json.load(open('out/tex_index.json'))
HSET=[H_DIFF,H_TEXS]
log=collections.defaultdict(list); stats={}
usedtex=set(); alpha_tex=collections.Counter()
for n in used:
    v=files[n]; raw,fl=(v if isinstance(v,tuple) else (v,None))
    dr=parse_ydr(raw,fl,frag=n.endswith('.yft'))
    gw=GW(); prims=[]
    for m in dr.models[:1]:
        for g in m:
            sh=dr.shaders[g['shader']] if g['shader']<len(dr.shaders) else None
            tn=None
            if sh:
                for h in HSET:
                    if sh['tex'].get(h): tn=sh['tex'][h]; break
            bucket=sh['bucket'] if sh else 0
            uri=None
            if tn:
                if tn in texidx: uri='../textures/%s.png'%tn; usedtex.add(tn)
                else: log['missing_texture'].append((n,tn))
            else: log['no_diffuse'].append(n)
            alpha='OPAQUE'; dbl=False
            if bucket==1: alpha='MASK'; dbl=True
            elif bucket in (2,3): alpha='BLEND'; dbl=(bucket==3)
            mat=gw.material(tn or 'untextured',uri,alpha,dbl)
            idx=g['idx'].reshape(-1,3)
            idx=idx[(idx[:,0]!=idx[:,1])&(idx[:,1]!=idx[:,2])&(idx[:,0]!=idx[:,2])].reshape(-1)
            prims.append(dict(pos=g['pos'],nrm=g['nrm'],uv=g['uv'],idx=idx,mat=mat))
    if not prims: log['empty'].append(n); continue
    mi=gw.mesh(n.rsplit('.',1)[0],prims); ni=gw.node(n.rsplit('.',1)[0],mesh=mi)
    gw.save(MAP+'/models/%s.gltf'%n.rsplit('.',1)[0],[ni])
    lo=np.array(dr.bbmin); hi=np.array(dr.bbmax)
    stats[n]=dict(tris=sum(len(p['idx'])//3 for p in prims),verts=sum(len(p['pos']) for p in prims),ext=float(np.ptp([lo,hi],0).max()),bmin=lo.tolist(),bmax=hi.tolist())
for t in usedtex: shutil.copy('out/tex/%s.png'%t,MAP+'/textures/%s.png'%t)
pickle.dump(stats,open('out/model_stats.pkl','wb'))
print('models exported',len(stats),'textures copied',len(usedtex))
print({k:len(v) for k,v in log.items()}); print(log['missing_texture'][:5])
json.dump({k:v for k,v in log.items()},open('out/export_log.json','w'))

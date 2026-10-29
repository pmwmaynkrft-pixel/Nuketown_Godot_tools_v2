import sys, os, re, pickle, json, math, collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from gltfw import *; from joaat import joaat; from rsc import load_rpf
PROJ=os.getcwd()+'/proj'; MAP=PROJ+'/maps/nuketown'
OFF=np.array([6000.0,10000.0,0.0])
files=load_rpf('ex/nuketown.rpf'); E=pickle.load(open('out/entities.pkl','rb')); S=pickle.load(open('out/model_stats.pkl','rb'))
byhash={joaat(n.rsplit('.',1)[0]):n for n in files}
# ---- collision gltf (one mesh per YBN cell) ----
cols=pickle.load(open('out/cols.pkl','rb'))
gw=GW(); roots=[]
mat=gw.material('collision',None)
for n,vs,tr in cols:
    nm=n.rsplit('.',1)[0].replace('nkt_','')   # col_28_25
    both=np.concatenate([tr,tr[:,::-1]]) # two-sided: source winding is not consistent
    mi=gw.mesh(nm,[dict(pos=(vs-OFF).astype(np.float32),idx=both.reshape(-1).astype(np.uint32),mat=mat)])
    roots.append(gw.node(nm+'-colonly',mesh=mi))
gw.save(MAP+'/collision/nuketown_collision.gltf',roots) if os.path.isdir(MAP+'/collision') else (os.makedirs(MAP+'/collision'),gw.save(MAP+'/collision/nuketown_collision.gltf',roots))
print('collision cells',len(roots))
# ---- scene ----
C=np.array([[1,0,0],[0,0,1],[0,-1,0]],float)
def qmat(q):
    x,y,z,w=q
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def cat(n,st):
    if 'mountain' in n: return 'Mountains'
    if n.endswith('.yft'): return 'Glass'
    if 'foliage' in n: return 'Foliage'
    if re.match(r'nkt_w_\d+_\d+',n): return 'Terrain'
    if st['ext']>=4: return 'Structures'
    return 'Props'
cats=['Terrain','Mountains','Structures','Props','Foliage','Glass']
model_ids={}; ext=[]
def mid(n):
    b=n.rsplit('.',1)[0]
    if b not in model_ids:
        model_ids[b]=len(model_ids)+1; ext.append('[ext_resource type="PackedScene" path="res://maps/nuketown/models/%s.gltf" id="%d"]'%(b,model_ids[b]))
    return model_ids[b]
nodes=collections.defaultdict(list); counts=collections.Counter(); tris=collections.Counter()
for k,e in enumerate(E):
    n=byhash[e['arch']]; st=S[n]; c=cat(n,st)
    q=e['q']; q=(-q[0],-q[1],-q[2],q[3])      # stored rotation is the inverse
    R=qmat(q)@np.diag([e['sxy'],e['sxy'],e['sz']])
    B=C@R@C.T; o=C@(np.array(e['pos'])-OFF)
    t='Transform3D(%s, %s)'%(', '.join('%.6g'%B[i][j] for i in range(3) for j in range(3)),', '.join('%.6g'%x for x in o))
    b=n.rsplit('.',1)[0]; nm='%s_%d'%(re.sub(r'^nkt_','',b)[:48],k)
    nodes[c].append('[node name="%s" parent="%s" instance=ExtResource("%d")]\ntransform = %s\n'%(nm,c,mid(n),t))
    counts[c]+=1; tris[c]+=st['tris']
ext.append('[ext_resource type="PackedScene" path="res://maps/nuketown/collision/nuketown_collision.gltf" id="%d"]'%(len(model_ids)+1)); colid=len(model_ids)+1
body=['[node name="Nuketown" type="Node3D"]\n']
for c in cats: body.append('[node name="%s" type="Node3D" parent="."]\n'%c)
for c in cats: body+=nodes[c]
body.append('[node name="Collision" parent="." instance=ExtResource("%d")]\n'%colid)
open('out/scene_body.txt','w').write('\n'.join(body))
open('out/scene_ext.txt','w').write('\n'.join(ext))
json.dump(dict(counts=counts,tris=tris),open('out/scene_stats.json','w'))
print(counts,tris,'models',len(model_ids))

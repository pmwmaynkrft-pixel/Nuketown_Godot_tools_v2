import json, struct, numpy as np, os
def g2gd(p):  # GTA (x,y,z) z-up -> Godot/glTF (x,z,-y) y-up
    p=np.asarray(p,dtype=np.float32); return np.stack([p[:,0],p[:,2],-p[:,1]],1)
class GW:
    def __init__(s): s.bin=bytearray(); s.bv=[]; s.acc=[]; s.meshes=[]; s.nodes=[]; s.mats=[]; s.images=[]; s.textures=[]; s.matkey={}; s.imgkey={}
    def _bv(s,data,target=None):
        while len(s.bin)%4: s.bin.append(0)
        o=len(s.bin); s.bin+=data; d=dict(buffer=0,byteOffset=o,byteLength=len(data))
        if target: d['target']=target
        s.bv.append(d); return len(s.bv)-1
    def _acc(s,arr,ctype,typ,target,minmax=False):
        bv=s._bv(arr.tobytes(),target)
        a=dict(bufferView=bv,componentType=ctype,count=len(arr),type=typ)
        if minmax: a['min']=arr.min(0).tolist(); a['max']=arr.max(0).tolist()
        s.acc.append(a); return len(s.acc)-1
    def image(s,uri):
        if uri not in s.imgkey:
            s.images.append(dict(uri=uri)); s.textures.append(dict(source=len(s.images)-1,sampler=0)); s.imgkey[uri]=len(s.textures)-1
        return s.imgkey[uri]
    def material(s,name,tex_uri,alpha='OPAQUE',double=False):
        k=(name,tex_uri,alpha,double)
        if k in s.matkey: return s.matkey[k]
        m=dict(name=name,pbrMetallicRoughness=dict(metallicFactor=0.0,roughnessFactor=0.9))
        if tex_uri: m['pbrMetallicRoughness']['baseColorTexture']=dict(index=s.image(tex_uri))
        if alpha!='OPAQUE': m['alphaMode']=alpha
        if alpha=='MASK': m['alphaCutoff']=0.5
        if double: m['doubleSided']=True
        s.mats.append(m); s.matkey[k]=len(s.mats)-1; return s.matkey[k]
    def mesh(s,name,prims):
        # prims: list of dict(pos,nrm,uv,idx,mat)
        ps=[]
        for p in prims:
            pos=g2gd(p['pos']); attrs=dict(POSITION=s._acc(pos.astype(np.float32),5126,'VEC3',34962,True))
            if p.get('nrm') is not None: attrs['NORMAL']=s._acc(g2gd(p['nrm']).astype(np.float32),5126,'VEC3',34962)
            if p.get('uv') is not None: attrs['TEXCOORD_0']=s._acc(np.ascontiguousarray(p['uv'],dtype=np.float32),5126,'VEC2',34962)
            idx=np.asarray(p['idx'],dtype=np.uint32)
            ia=s._acc(idx if idx.max()>65535 else idx.astype(np.uint16),5125 if idx.max()>65535 else 5123,'SCALAR',34963)
            ps.append(dict(attributes=attrs,indices=ia,material=p['mat']))
        s.meshes.append(dict(name=name,primitives=ps)); return len(s.meshes)-1
    def node(s,name,mesh=None,t=None,q=None,sc=None,children=None):
        n=dict(name=name)
        if mesh is not None: n['mesh']=mesh
        if t is not None: n['translation']=[float(x) for x in t]
        if q is not None: n['rotation']=[float(x) for x in q]
        if sc is not None: n['scale']=[float(x) for x in sc]
        if children: n['children']=children
        s.nodes.append(n); return len(s.nodes)-1
    def save(s,path,roots=None):
        base=os.path.splitext(path)[0]
        j=dict(asset=dict(version='2.0',generator='nuketown-extract'),scene=0,scenes=[dict(nodes=roots if roots is not None else list(range(len(s.nodes))))],
               nodes=s.nodes,meshes=s.meshes,materials=s.mats,images=s.images,textures=s.textures,samplers=[dict(magFilter=9729,minFilter=9987,wrapS=10497,wrapT=10497)],
               accessors=s.acc,bufferViews=s.bv,buffers=[dict(uri=os.path.basename(base)+'.bin',byteLength=len(s.bin))])
        open(base+'.bin','wb').write(bytes(s.bin)); open(path,'w').write(json.dumps(j))

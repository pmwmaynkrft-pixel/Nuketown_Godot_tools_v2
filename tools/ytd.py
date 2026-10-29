import struct, io, os, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from rsc import *
from PIL import Image
def cstr(d,o):
    e=d.index(b'\0',o); return d[o:e].decode('latin1')
def fmt_name(f):
    if f<256: return 'code%d'%f
    return struct.pack('<I',f).decode('latin1')
def block_size(fmt,w,h):
    if fmt in ('DXT1','ATI1'): return max(1,(w+3)//4)*max(1,(h+3)//4)*8
    if fmt in ('DXT3','DXT5','ATI2','BC7 '): return max(1,(w+3)//4)*max(1,(h+3)//4)*16
    return None
def read_ytd(path_or_tuple):
    v=path_or_tuple
    raw,fl=(v if isinstance(v,tuple) else (v,None))
    r=Res(raw,fl); d=r.data
    lp=struct.unpack_from('<Q',d,0x30)[0]&0xfffffff
    cnt=struct.unpack_from('<H',d,0x38)[0]
    texs=[]
    for i in range(cnt):
        p=struct.unpack_from('<Q',d,lp+i*8)[0]
        o=p&0xfffffff
        nm=cstr(d,struct.unpack_from('<Q',d,o+0x28)[0]&0xfffffff)
        w,h,dep,stride=struct.unpack_from('<4H',d,o+0x50)
        f=struct.unpack_from('<I',d,o+0x58)[0]
        levels=d[o+0x5D]
        dp=struct.unpack_from('<Q',d,o+0x70)[0]
        b,x=r.at(dp)
        texs.append(dict(name=nm,w=w,h=h,fmt=f,fmtname=fmt_name(f),levels=levels,stride=stride,off=x,data=b))
    return texs
def to_image(t):
    f=t['fmtname']; w,h=t['w'],t['h']
    if f in ('DXT1','DXT3','DXT5','ATI1','ATI2','BC7 '):
        n=block_size(f,w,h); body=t['data'][t['off']:t['off']+n]
        if f=='BC7 ':
            hdr=b'DDS '+struct.pack('<7I',124,0x1007,h,w,n,0,1)+b'\0'*44+struct.pack('<II4s5I',32,4,b'DX10',0,0,0,0,0)+struct.pack('<5I',0x1000,0,0,0,0)+struct.pack('<5I',98,3,0,1,0)
        elif f in('ATI1','ATI2'):
            dxgi=80 if f=='ATI1' else 83
            hdr=b'DDS '+struct.pack('<7I',124,0x1007,h,w,n,0,1)+b'\0'*44+struct.pack('<II4s5I',32,4,b'DX10',0,0,0,0,0)+struct.pack('<5I',0x1000,0,0,0,0)+struct.pack('<5I',dxgi,3,0,1,0)
        else:
            hdr=b'DDS '+struct.pack('<7I',124,0x81007,h,w,n,0,1)+b'\0'*44+struct.pack('<II4s5I',32,4,f.encode(),0,0,0,0,0)+struct.pack('<5I',0x1000,0,0,0,0)
        return Image.open(io.BytesIO(hdr+body)).convert('RGBA')
    if f in ('code21','code32'):
        n=w*h*4; body=t['data'][t['off']:t['off']+n]
        return Image.frombytes('RGBA',(w,h),body,'raw','BGRA')
    raise ValueError(f)
if __name__=='__main__':
    os.makedirs('out/tex',exist_ok=True)
    tex=load_rpf('ex/nuketown_tex.rpf')
    allt={}
    from collections import Counter
    fm=Counter(); fails=[]
    for n,v in tex.items():
        for t in read_ytd(v):
            fm[(t['fmtname'])]+=1
            try:
                im=to_image(t); im.save('out/tex/%s.png'%t['name']); allt[t['name']]=(n,t['w'],t['h'],t['fmtname'])
            except Exception as e:
                fails.append((n,t['name'],t['fmtname'],str(e)[:60]))
    print('formats',dict(fm)); print('ok',len(allt),'fail',len(fails)); print(fails[:10])
    import json; json.dump(allt,open('out/tex_index.json','w'))

import struct, sys, os
def parse(buf, base=0):
    magic,cnt,nlen,enc=struct.unpack_from('<4sIII',buf,base)
    assert magic==b'7FPR', magic
    ents=[]
    for i in range(cnt):
        a,b,c,d=struct.unpack_from('<IIII',buf,base+16+i*16)
        ents.append((a,b,c,d))
    nt=base+16+cnt*16
    names=buf[nt:nt+nlen]
    def nm(o):
        e=names.index(b'\0',o); return names[o:e].decode('latin1')
    out=[]
    for i,(a,b,c,d) in enumerate(ents):
        name_off=a&0xFFFF
        if b==0x7FFFFF00:  # directory
            out.append(dict(i=i,dir=True,name=nm(a&0xFFFF) if i else '',first=c,count=d))
        else:
            # file entry: name(2) size(3) offset(3) | sys flags | gfx flags
            name_off=struct.unpack_from('<H',buf,base+16+i*16)[0]
            sz=buf[base+16+i*16+2]|(buf[base+16+i*16+3]<<8)|(buf[base+16+i*16+4]<<16)
            off=buf[base+16+i*16+5]|(buf[base+16+i*16+6]<<8)|(buf[base+16+i*16+7]<<16)
            sysf,gfxf=c,d
            out.append(dict(i=i,dir=False,name=nm(name_off),size=sz,off=off,sysf=sysf,gfxf=gfxf))
    return enc,out
def tree(out):
    res=[]
    def walk(i,path):
        e=out[i]
        for j in range(e['first'],e['first']+e['count']):
            c=out[j]
            p=path+'/'+c['name']
            if c['dir']: walk(j,p)
            else: res.append((p,c))
    walk(0,'')
    return res
if __name__=='__main__':
    buf=open(sys.argv[1],'rb').read()
    enc,out=parse(buf)
    for p,c in tree(out):
        print(p,c['size'],c['off'],hex(c['sysf']),hex(c['gfxf']))

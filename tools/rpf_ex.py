import sys, os, struct, zlib
from rpf7 import parse, tree
def extract(buf, base, outdir, prefix=''):
    enc,out=parse(buf,base)
    results=[]
    for p,c in tree(out):
        offraw=c['off']
        isres = bool(offraw & 0x800000)
        off=(offraw & 0x7FFFFF)*512
        if not isres:
            comp=c['size']; unc=c['sysf']; e=c['gfxf']
            ln = comp if comp else unc
            data=buf[base+off: base+off+ln]
            if comp and comp!=unc and e==0:
                try: data=zlib.decompress(data,-15)
                except Exception as ex: data=data
            results.append((prefix+p,'bin',e,data))
        else:
            results.append((prefix+p,'res',c['sysf'],(base+off,c['size'],c['sysf'],c['gfxf'])))
    return enc,results
if __name__=='__main__':
    buf=open(sys.argv[1],'rb').read()
    enc,res=extract(buf,0,None)
    for p,k,a,d in res:
        print(p,k,hex(a) if isinstance(a,int) else a, len(d) if k=='bin' else d)

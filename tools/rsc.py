import os
import struct, zlib
from rpf_ex import extract
def size_from_flags(f):
    s0=((f>>27)&1)<<0; s1=((f>>26)&1)<<1; s2=((f>>25)&1)<<2; s3=((f>>24)&1)<<3
    s4=((f>>17)&0x7F)<<4; s5=((f>>11)&0x3F)<<5; s6=((f>>7)&0xF)<<6; s7=((f>>5)&3)<<7; s8=((f>>4)&1)<<8
    ss=f&0xF
    return (0x200<<ss)*(s0+s1+s2+s3+s4+s5+s6+s7+s8)
class Res:
    def __init__(s, raw, flags=None):
        magic,ver,sf,gf=struct.unpack_from('<IIII',raw,0)
        if flags: sf,gf=flags
        else: assert magic==0x37435352, hex(magic)
        s.ver=ver; s.sf=sf; s.gf=gf
        s.sys_size=size_from_flags(sf); s.gfx_size=size_from_flags(gf)
        d=zlib.decompressobj(-15).decompress(raw[16:])
        s.data=d
        s.sys=d[:s.sys_size]; s.gfx=d[s.sys_size:s.sys_size+s.gfx_size]
    def at(s,ptr):
        seg=ptr>>28; off=ptr&0x0FFFFFFF
        if seg==5: return s.data, off
        if seg==6: return s.data, s.sys_size+off
        raise ValueError(hex(ptr))
    def u32(s,ptr,o=0):
        b,x=s.at(ptr); return struct.unpack_from('<I',b,x+o)[0]
    def u64(s,ptr,o=0):
        b,x=s.at(ptr); return struct.unpack_from('<Q',b,x+o)[0]
    def u16(s,ptr,o=0):
        b,x=s.at(ptr); return struct.unpack_from('<H',b,x+o)[0]
    def f32(s,ptr,o=0):
        b,x=s.at(ptr); return struct.unpack_from('<f',b,x+o)[0]
    def bytes(s,ptr,n,o=0):
        b,x=s.at(ptr); return b[x+o:x+o+n]
def load_rpf(path):
    buf=open(path,'rb').read()
    enc,res=extract(buf,0,None)
    out={}
    for p,k,a,d in res:
        if k=='res':
            off,size,sf,gf=d
            if size==0xFFFFFF:
                # large resource: size stored in header? take until next offset
                raw=buf[off:]  # decompressor stops at stream end
            else:
                raw=buf[off:off+size]
            out[p.lstrip('/')]=(raw,(sf,gf)) if size==0xFFFFFF else raw
        else:
            out[p.lstrip('/')]=d
    return out

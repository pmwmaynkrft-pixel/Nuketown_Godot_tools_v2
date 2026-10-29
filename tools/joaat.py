import os
def joaat(s):
    h=0
    for c in s.lower().encode('latin1'):
        h=(h+c)&0xFFFFFFFF; h=(h+(h<<10))&0xFFFFFFFF; h^=(h>>6)
    h=(h+(h<<3))&0xFFFFFFFF; h^=(h>>11); h=(h+(h<<15))&0xFFFFFFFF
    return h

#!/usr/bin/env python3
"""Xref scan MIPS32 LE: cuenta referencias lui/addiu|ori a direcciones de strings dadas."""
import struct, sys, subprocess, re

def sections(p):
    out = subprocess.run(["readelf","-S","-W",p],capture_output=True,text=True).stdout
    S={}
    for m in re.finditer(r"\[\s*\d+\]\s+(\S+)\s+\S+\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)",out):
        S[m.group(1)]=(int(m.group(2),16),int(m.group(3),16),int(m.group(4),16))
    return S

def strtab(p, S, names):
    """devuelve {name: [vaddr,...]} buscando el string NUL-terminado en el archivo"""
    data=open(p,'rb').read()
    res={n:[] for n in names}
    for n in names:
        pat=(n+"\0").encode()
        i=0
        while True:
            i=data.find(pat,i)
            if i<0: break
            # mapear file offset -> vaddr
            for sn,(addr,off,size) in S.items():
                if off<=i<off+size and addr:
                    res[n].append((sn,addr+(i-off)))
                    break
            i+=1
    return res

def xrefs(p,S,targets):
    addr,off,size=S['.text']
    data=open(p,'rb').read()[off:off+size]
    hi={}   # reg -> (imm16, pc)
    found={t:[] for t in targets}
    tset=set(targets)
    for i in range(0,len(data)-3,4):
        w=struct.unpack_from("<I",data,i)[0]
        op=w>>26
        pc=addr+i
        if op==0x0f:  # lui rt, imm
            rt=(w>>16)&31; imm=w&0xffff
            hi[rt]=(imm,pc)
        elif op in (0x09,0x0d,0x23,0x28,0x2b,0x21,0x25,0x20,0x24):  # addiu/ori/lw/sw/lh/lhu/lb/lbu
            rs=(w>>21)&31; rt=(w>>16)&31; imm=w&0xffff
            if rs in hi:
                h=hi[rs][0]
                if op==0x0d:  # ori: zero-extend
                    a=(h<<16)|imm
                else:
                    a=((h<<16)+struct.unpack("<h",struct.pack("<H",imm))[0])&0xffffffff
                if a in tset:
                    found[a].append((hi[rs][1],pc))
            if op in (0x09,0x0d,0x23) and rt!=rs:
                hi.pop(rt,None)
            elif op in (0x09,0x0d) and rt==rs:
                hi.pop(rt,None)
    return found

if __name__=="__main__":
    p=sys.argv[1]; names=sys.argv[2:]
    S=sections(p)
    locs=strtab(p,S,names)
    tmap={}
    for n,l in locs.items():
        for sec,va in l:
            tmap[va]=(n,sec)
    fx=xrefs(p,S,list(tmap.keys()))
    for va,(n,sec) in sorted(tmap.items(), key=lambda kv: kv[1][0]):
        r=fx[va]
        print(f"{n:38s} {sec:12s} 0x{va:08x}  xrefs={len(r)}  {[hex(x[1]) for x in r[:6]]}")

#!/usr/bin/env python3
"""Mini-desensamblador MIPS32 LE: solo lo necesario para leer el contexto de un xref (lui/addiu/lw/jal/...)."""
import struct, sys, subprocess, re
R=["zero","at","v0","v1","a0","a1","a2","a3","t0","t1","t2","t3","t4","t5","t6","t7",
   "s0","s1","s2","s3","s4","s5","s6","s7","t8","t9","k0","k1","gp","sp","fp","ra"]
OPI={0x08:"addi",0x09:"addiu",0x0a:"slti",0x0b:"sltiu",0x0c:"andi",0x0d:"ori",0x0e:"xori",
     0x20:"lb",0x21:"lh",0x23:"lw",0x24:"lbu",0x25:"lhu",0x28:"sb",0x29:"sh",0x2b:"sw",0x0f:"lui"}
FUN={0x00:"sll",0x02:"srl",0x03:"sra",0x04:"sllv",0x06:"srlv",0x08:"jr",0x09:"jalr",0x0c:"syscall",
     0x10:"mfhi",0x12:"mflo",0x18:"mult",0x19:"multu",0x1a:"div",0x1b:"divu",
     0x21:"addu",0x23:"subu",0x24:"and",0x25:"or",0x26:"xor",0x27:"nor",0x2a:"slt",0x2b:"sltu"}
def sections(p):
    out=subprocess.run(["readelf","-S","-W",p],capture_output=True,text=True).stdout
    S={}
    for m in re.finditer(r"\[\s*\d+\]\s+(\S+)\s+\S+\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)",out):
        S[m.group(1)]=(int(m.group(2),16),int(m.group(3),16),int(m.group(4),16))
    return S
def dis(p,start,n=48):
    S=sections(p); a,o,sz=S['.text']; d=open(p,'rb').read()
    for i in range(n):
        pc=start+i*4; off=o+(pc-a)
        w=struct.unpack_from("<I",d,off)[0]
        op=w>>26; rs=(w>>21)&31; rt=(w>>16)&31; rd=(w>>11)&31; sa=(w>>6)&31; fn=w&63
        imm=struct.unpack("<h",struct.pack("<H",w&0xffff))[0]
        if w==0: s="nop"
        elif op==0: 
            f=FUN.get(fn,f"fn{fn:02x}")
            s=f"{f} {R[rd]},{R[rs]},{R[rt]}" if f not in("jr","jalr","sll","srl","sra","mfhi","mflo","mult","multu","div","divu") else (
               f"{f} {R[rs]}" if f in("jr",) else f"{f} {R[rd]},{R[rt]},{sa}" if f in("sll","srl","sra") else f"{f} {R[rd]}" if f in("mfhi","mflo") else f"{f} {R[rs]},{R[rt]}")
        elif op==2: s=f"j 0x{((pc+4)&0xf0000000)|((w&0x3ffffff)<<2):08x}"
        elif op==3: s=f"jal 0x{((pc+4)&0xf0000000)|((w&0x3ffffff)<<2):08x}"
        elif op==4: s=f"beq {R[rs]},{R[rt]},0x{pc+4+imm*4:08x}"
        elif op==5: s=f"bne {R[rs]},{R[rt]},0x{pc+4+imm*4:08x}"
        elif op==6: s=f"blez {R[rs]},0x{pc+4+imm*4:08x}"
        elif op==7: s=f"bgtz {R[rs]},0x{pc+4+imm*4:08x}"
        elif op==1: s=f"bltz/bgez {R[rs]},0x{pc+4+imm*4:08x}"
        elif op==0x0f: s=f"lui {R[rt]},0x{w&0xffff:04x}"
        elif op in OPI:
            m=OPI[op]
            s=f"{m} {R[rt]},{imm}({R[rs]})" if op>=0x20 else f"{m} {R[rt]},{R[rs]},{imm}"
        else: s=f".word 0x{w:08x} (op{op:02x})"
        print(f"  {pc:08x}: {w:08x}  {s}")
if __name__=="__main__":
    dis(sys.argv[1], int(sys.argv[2],16), int(sys.argv[3]) if len(sys.argv)>3 else 48)

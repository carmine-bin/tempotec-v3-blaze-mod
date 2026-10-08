"""Generate the validated UI payload from the pinned Full Mod player and layouts.

No release source or input firmware is overwritten. Layouts retain duplicate keys.
The small assembler deliberately supports only instructions used in hooks.S.
"""
from pathlib import Path
import ast
import hashlib
import json
import re
import struct
import sys

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'build/v1.3'))
from layout import P, load, nodes, get, setv, encode, validate_order

BASE = 0x907040
PLAYER_SHA = 'ab7623fb8ea21e410068a12b484fcb848eff829eaa190774c58f7d371d2913b4'
R = {n:i for i,n in enumerate('zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp fp ra'.split())}
ENTER = ['addiu sp, sp, -48', 'sw ra, 44(sp)', 'sw s0, 40(sp)',
         'sw s1, 36(sp)', 'sw s2, 32(sp)', 'sw s3, 28(sp)']
LEAVE = ['lw ra, 44(sp)', 'lw s0, 40(sp)', 'lw s1, 36(sp)',
         'lw s2, 32(sp)', 'lw s3, 28(sp)', 'jr ra', 'addiu sp, sp, 48']

def assemble(source):
    labels, lines, pc = {}, [], BASE
    for raw in source.splitlines():
        line = raw.split('#', 1)[0].strip()
        if not line: continue
        if line.endswith(':'):
            assert line[:-1] not in labels
            labels[line[:-1]] = pc
            continue
        for line in ENTER if line == 'enter' else LEAVE if line == 'leave' else [line]:
            if line.startswith('.asciiz '):
                value = ast.literal_eval(line[8:]).encode() + b'\0'
                lines.append((pc, value)); pc += len(value)
            else:
                lines.append((pc, line)); pc += 8 if line.startswith('li ') else 4
    def val(s): return labels[s] if s in labels else int(s, 0)
    def iw(op, rs, rt, imm):
        assert -32768 <= imm <= 65535
        return op << 26 | R[rs] << 21 | R[rt] << 16 | (imm & 65535)
    output, listing = bytearray(), []
    for pc, line in lines:
        if isinstance(line, bytes): output.extend(line); continue
        p = re.split(r'[\s,()]+', line); op, a = p[0], [x for x in p[1:] if x]
        if op == 'li':
            v = val(a[1]); words = [iw(15, 'zero', a[0], v >> 16), iw(13, a[0], a[0], v & 65535)]
        elif op == 'nop': words = [0]
        elif op in ('move', 'slt'):
            rd, rs = a[:2]; rt = 'zero' if op == 'move' else a[2]
            words = [R[rs] << 21 | R[rt] << 16 | R[rd] << 11 | (0x25 if op == 'move' else 0x2a)]
        elif op == 'jr': words = [R[a[0]] << 21 | 8]
        elif op == 'jalr': words = [R[a[0]] << 21 | R['ra'] << 11 | 9]
        elif op == 'sll':
            rd, rt, sa = a; assert 0 <= int(sa, 0) < 32
            words = [R[rt] << 16 | R[rd] << 11 | int(sa, 0) << 6]
        elif op == 'addu':
            rd, rs, rt = a; words = [R[rs] << 21 | R[rt] << 16 | R[rd] << 11 | 0x21]
        elif op in ('j', 'jal'):
            target = val(a[0]); assert target % 4 == 0 and target >> 28 == (pc+4) >> 28
            words = [(2 if op == 'j' else 3) << 26 | target >> 2]
        elif op in ('beq', 'bne', 'b', 'bltz', 'bgez'):
            if op == 'b': rs, rt, target, opc = 'zero', 'zero', a[0], 4
            elif op in ('beq', 'bne'): rs, rt, target = a; opc = 4 if op == 'beq' else 5
            else: rs, target = a; rt, opc = ('zero' if op == 'bltz' else 'at'), 1
            delta = val(target)-pc-4; assert delta % 4 == 0 and -32768 <= delta//4 <= 32767
            words = [iw(opc, rs, rt, delta//4)]
        elif op in ('lw', 'sw', 'lbu'):
            rt, imm, rs = a; words = [iw({'lw':35, 'sw':43, 'lbu':36}[op], rs, rt, val(imm))]
        elif op == 'lui': words = [iw(15, 'zero', a[0], val(a[1]))]
        elif op == 'addiu': words = [iw(9, a[1], a[0], val(a[2]))]
        else: raise ValueError(line)
        for i,w in enumerate(words):
            output.extend(struct.pack('<I',w)); listing.append({'va':pc+4*i,'word':w,'source':line})
    # Reject a pseudo-instruction split across a control transfer's delay slot.
    bypc = {pc:line for pc,line in lines}
    for pc,line in lines:
        if isinstance(line,str) and line.split()[0] in ('j','jal','jr','jalr','b','beq','bne','bltz','bgez'):
            assert isinstance(bypc.get(pc+4),str) and not bypc[pc+4].startswith('li '), (hex(pc),line)
    return bytes(output), labels, listing

def patch_player(data):
    assert hashlib.sha256(data).hexdigest() == PLAYER_SHA
    code, labels, listing = assemble((Path(__file__).parent/'hooks.S').read_text())
    b, changes = bytearray(data), []
    def change(offset, old, new, bug, description):
        assert b[offset:offset+len(old)] == old, (hex(offset), description)
        assert len(old) == len(new)
        b[offset:offset+len(old)] = new
        changes.append(dict(offset=offset, va=offset+0x400000 if offset>=0x214a0 else None,
                            before=old.hex(), after=new.hex(), bug=bug, description=description))
    def hook(va, old, label, bug, call=False):
        words = struct.pack('<I', (3 if call else 2)<<26 | labels[label]>>2)
        old = bytes.fromhex(old)
        change(va-0x400000,old,words+bytes(len(old)-4),bug,label)
    hook(0x4dfbf4,'6087130c','list_header',2,True)
    hook(0x4e5990,'109c130c','add_header',2,True)
    hook(0x50dcb8,'2039140c','eq_header',2,True)
    hook(0x4b49a8,'e10140048300053c','list_geometry',2)
    change(0xca0b4,bytes.fromhex('ecff0224'),bytes.fromhex('00000224'),2,'Add: remove hidden-bar -20 header move')
    hook(0x4f5718,'50351108','color_reload',3)
    hook(0x5157c8,'120020128300053c','color_restore',3)
    hook(0x4e2e5c,'c8bc110c','settings_repaint',4,True)
    # Battery frame follows the state image (jalr $25 -> jal; delay-slot nop kept).
    assert data[0x10c20c:0x10c210] == bytes(4) and data[0x10cb1c:0x10cb20] == bytes(4)
    hook(0x50c208,'09f82003','battery_state',5,True)
    hook(0x50cb18,'09f82003','battery_normal',5,True)
    # Next-track cover prefetch (getter case 31, only with tf_image_cache_enable)
    # peeks through the real advance routine; on an album's last track that
    # stops playback. Drop the call: the zeroed buffer makes both sites skip.
    for va in (0x518320,0x51d25c):
        assert data[va-0x400000+4:va-0x400000+8] == bytes.fromhex('1f000424')
        change(va-0x400000,bytes.fromhex('58e0100c'),bytes(4),6,'Skip next-track cover prefetch')
    assert not any(data[0x507030:0x508000])
    assert BASE-0x400000+len(code) <= 0x508000
    change(BASE-0x400000,bytes(len(code)),code,'shared','UI hooks in verified unallocated file gap')
    phoff = struct.unpack_from('<I',data,28)[0]
    phsize, phnum = struct.unpack_from('<HH',data,42)
    loads = []
    for i in range(phnum):
        off = phoff+i*phsize; p = struct.unpack_from('<8I',data,off)
        if p[0] == 1: loads.append((off,p))
    off,p = loads[0]
    assert p == (1,0,0x400000,0x400000,0x507030,0x507030,5,0x10000)
    end = BASE-0x400000+len(code)
    assert loads[1][1][1] >= end and loads[1][1][2] >= end+0x400000
    change(off+16,struct.pack('<II',p[4],p[5]),struct.pack('<II',end,end),'shared','Extend existing RX load span over UI hooks')
    assert b[0x38240:0x38244] == bytes(4)
    return bytes(b), {'patches':changes,'labels':labels,'instructions':listing,
                     'before_sha256':PLAYER_SHA,'after_sha256':hashlib.sha256(b).hexdigest()}

def resources(root, out):
    base = root/'usr/resource/layout/theme1'
    dest = out/'usr/resource/layout/theme1'; dest.mkdir(parents=True,exist_ok=True)
    changed = {}
    def write(rel, doc, bug):
        validate_order(doc)
        p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(encode(doc)+'\n')
        changed['usr/resource/layout/theme1/'+rel]=bug
    # Entire shutdown surface, with existing art and text at identical screen coordinates.
    doc=load(base/'dialog/shutdown_timer.dlg'); n=nodes(doc); r=n['vg_dialog_shutdown_timer']['node']
    img=get(r,'img_path'); r[:]=[(k,v) for k,v in r if k!='img_path']
    r.insert(0,('imageview',P([('name','ui_shutdown_background'),('img_path',img),('x',0),('y',20),('imageview',True)])))
    for name in ['shutdown_timer_tv_msg','shutdown_timer_tv_count']:
        x=n[name]['node'];setv(x,'y',get(x,'y')+20)
    for k,v in [('h',480),('hglview_y',0),('hglview_h',480),('color','0x000000')]:setv(r,k,v)
    write('dialog/shutdown_timer.dlg',doc,1)
    # Separate resources: ordinary settings/library entry keeps its original header.
    for original, new, rootname in [('hiby_sub_back.view','ui_sub_back.view','vg_sub_back_hiby'),
                                    ('hiby_set_sub_back.view','ui_set_sub_back.view','vg_set_sub_back_hiby'),
                                    ('hiby_eq_title.view','ui_eq_title.view','vg_eq_title_hiby')]:
        doc=load(base/original); n=nodes(doc); r=n[rootname]['node']
        for obj in n.values():
            if obj['parent']==rootname:
                x=obj['node'];setv(x,'y',get(x,'y',0)+30)
                if get(x,'touch_y') is not None:setv(x,'touch_y',get(x,'touch_y')+30)
        for k,v in [('h',68),('hglview_y',0),('hglview_h',68)]:setv(r,k,v)
        write(new,doc,2)
    # Properties owns a full-screen dialog. Reserve 30px above its header;
    # reclaim the existing 3px gaps in ten metadata rows so Path keeps its bounds.
    doc=load(base/'dialog/playmenu_song_info.dlg');n=nodes(doc)
    for name in ['playmenu_song_info_tv_title','playmenu_song_info_tv_artist','iv_back']:
        x=n[name]['node'];setv(x,'y',get(x,'y')+30)
        if get(x,'touch_y') is not None:setv(x,'touch_y',get(x,'touch_y')+30)
    for obj in n.values():
        x=obj['node'];name=get(x,'name','');y=get(x,'y')
        if (obj['parent']=='playmenu_song_info_vg' and y is not None and 40<=y<=388
                and name not in ('playmenu_song_info_tv_title','playmenu_song_info_tv_artist')):
            row=(y-40)//35
            setv(x,'y',y+30-3*row-(2 if obj['kind']=='imageview' else 0))
    setv(n['playmenu_song_info_vg']['node'],'h',480)
    write('dialog/playmenu_song_info.dlg',doc,2)
    return changed

def generate(root, out):
    out.mkdir(parents=True,exist_ok=True)
    changes=resources(root,out)
    data,record=patch_player((root/'usr/bin/hiby_player').read_bytes())
    p=out/'usr/bin/hiby_player';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    changes['usr/bin/hiby_player']=[2,3,4,6]
    return changes,record

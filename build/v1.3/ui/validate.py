"""Independent LLVM assembly and execution checks for the validated MIPS hooks."""
from pathlib import Path
import re, struct, subprocess, json
from . import patch

class Machine:
    def __init__(self, code, labels, player):
        self.labels=labels;self.mem={patch.BASE+i:v for i,v in enumerate(code)};self.player=player
        self.r=[0]+[0x11000000+i*256 for i in range(1,32)];self.r[29]=0x300000;self.r[31]=0xff0000
        self.calls=[];self.writes=[];self.hidden=False;self.resolve_status=0;self.pc=0;self.frame_entry=0
    def byte(self,a):
        if a in self.mem:return self.mem[a]
        off=a-0x400000
        if 0<=off<0x507030:return self.player[off]
        return 0
    def word(self,a):return sum(self.byte(a+i)<<(8*i) for i in range(4))
    def put(self,a,v):
        for i in range(4):self.mem[a+i]=(v>>(8*i))&255
    def string(self,a):
        v=bytearray()
        for i in range(1024):
            c=self.byte(a+i)
            if not c:return bytes(v)
            v.append(c)
        raise AssertionError('unterminated string')
    def putstr(self,a,v):
        for i,c in enumerate(v+b'\0'):self.mem[a+i]=c
    def external(self,a):
        args=self.r[4:8];self.calls.append((a,args.copy()));v=0
        if a==0x449d00:
            assert self.string(args[1])==b'vg_topbar';v=0x4000000
            self.put(v+4,-320 if self.hidden else 0)
        elif a==0x9064e0:v=0 if self.string(args[0])==self.string(args[1]) else 1
        elif a==0x906f70:
            value=self.string(args[1]);self.putstr(args[0],value);v=args[0]
        elif a in (0x4e1d80,0x4e7040,0x50e480):v=self.resolve_status
        elif a in (0x430e60,0x44d360,0x514ec0,0x46f320):v=123
        elif a==0x4a1b80:
            assert self.string(args[1])==b'topbar_iv_battery_frame' and self.string(args[2])==b'imageview'
            v=self.frame_entry
        elif a in (0x260000,0x270000):pass
        else:raise AssertionError(hex(a))
        # Model permitted ABI clobbers so wrappers cannot depend on scratch values.
        for i in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,24,25]:self.r[i]=0xdead0000+i
        self.r[2]=v;self.pc=self.r[31]
    def instruction(self,a):
        w=self.word(a);op=w>>26;rs=(w>>21)&31;rt=(w>>16)&31;rd=(w>>11)&31;im=w&65535;s=im if im<32768 else im-65536
        target=None
        if w==0:pass
        elif op==0:
            f=w&63
            if f==0x25:self.r[rd]=self.r[rs]|self.r[rt]
            elif f==0x21:self.r[rd]=(self.r[rs]+self.r[rt])&0xffffffff
            elif f==0:self.r[rd]=(self.r[rt]<<((w>>6)&31))&0xffffffff
            elif f==9:target=self.r[rs];self.r[rd]=a+8
            elif f==0x2a:self.r[rd]=int(self.signed(self.r[rs])<self.signed(self.r[rt]))
            elif f==8:target=self.r[rs]
            else:raise AssertionError(hex(w))
        elif op==9:self.r[rt]=(self.r[rs]+s)&0xffffffff
        elif op==15:self.r[rt]=im<<16
        elif op==13:self.r[rt]=self.r[rs]|im
        elif op in (35,36):
            addr=(self.r[rs]+s)&0xffffffff;self.r[rt]=self.word(addr) if op==35 else self.byte(addr)
        elif op==43:
            addr=(self.r[rs]+s)&0xffffffff;self.put(addr,self.r[rt]);self.writes.append(addr)
        elif op in (2,3):
            target=((a+4)&0xf0000000)|((w&0x3ffffff)<<2)
            if op==3:self.r[31]=a+8
        elif op in (4,5,1):
            yes=(self.r[rs]==self.r[rt]) if op==4 else (self.r[rs]!=self.r[rt]) if op==5 else (self.signed(self.r[rs])<0 if rt==0 else self.signed(self.r[rs])>=0)
            target=a+4+s*4 if yes else a+8
        else:raise AssertionError(hex(w))
        self.r[0]=0;return target
    @staticmethod
    def signed(v):return v if v<0x80000000 else v-0x100000000
    def run(self,label,stops=()):
        self.pc=self.labels[label];before=self.r.copy()
        for count in range(2000):
            if self.pc in stops or self.pc==0xff0000:return before,self.pc
            if not patch.BASE<=self.pc<self.labels['sub_filename']:
                self.external(self.pc);continue
            a=self.pc;t=self.instruction(a)
            if t is not None:
                assert self.instruction(a+4) is None,'control transfer in delay slot'
                self.pc=t
            else:self.pc=a+4
        raise AssertionError('execution did not terminate')
    def abi(self,before):
        assert self.r[16:24]==before[16:24] and self.r[28:31]==before[28:31]
        assert self.r[31]==before[31]

def llvm_check(source, code, labels, out):
    lines=['.text','.set noreorder','.set noat']
    for raw in source.splitlines():
        line=raw.split('#',1)[0].strip()
        if not line:continue
        for x in patch.ENTER if line=='enter' else patch.LEAVE if line=='leave' else [line]:
            if x.startswith('li '):
                reg,value=re.split(r'[ ,]+',x)[1:];v=labels[value] if value in labels else int(value,0)
                xs=[f'lui {reg}, {v>>16}',f'ori {reg}, {reg}, {v&65535}']
            else:xs=[x]
            for x in xs:
                if x.startswith(('j ','jal ')):
                    op,value=x.split();x=op+' '+hex(labels[value]) if value in labels else x
                if not x.startswith('.asciiz'):
                    x=re.sub(r'\b('+'|'.join(patch.R)+r')\b',r'$\1',x)
                lines.append(x)
    asm=out/'llvm-hooks.S';obj=out/'llvm-hooks.o';asm.write_text('\n'.join(lines)+'\n')
    subprocess.run(['clang','-target','mipsel-linux-gnu','-march=mips32','-mno-abicalls','-fno-pic','-c',str(asm),'-o',str(obj)],check=True)
    elf=obj.read_bytes();shoff=struct.unpack_from('<I',elf,32)[0];size,n,strings=struct.unpack_from('<HHH',elf,46)
    sections=[struct.unpack_from('<10I',elf,shoff+i*size) for i in range(n)]
    names=elf[sections[strings][4]:sections[strings][4]+sections[strings][5]]
    text=next(s for s in sections if names[s[0]:].split(b'\0')[0]==b'.text')
    actual=elf[text[4]:text[4]+text[5]]
    assert actual[:len(code)]==code,[(hex(patch.BASE+i),a,b) for i,(a,b) in enumerate(zip(actual,code)) if a!=b][:8]
    assert not any(actual[len(code):])
    assert not any(s[1] in (4,9) and s[7]==sections.index(text) for s in sections),'unresolved text relocation'
    return len(code)

def validate(root,overlay,out):
    source=Path(__file__).with_name('hooks.S').read_text();code,labels,_=patch.assemble(source)
    player=(root/'usr/bin/hiby_player').read_bytes();checks=[]
    llvm_check(source,code,labels,out);checks.append('LLVM MIPS32 assembly byte-identical, no relocations')
    def new():return Machine(code,labels,player)
    for hidden in (False,True):
        for ident in range(123):
            m=new();m.hidden=hidden;m.r[4]=0x200000;m.r[6]=0x210000;m.put(m.r[4]+64,ident);m.put(m.r[4]+216,0x220000)
            m.putstr(0x210000,b'usr\\resource\\layout\\theme1\\hiby_sub_back.view');contract=bytes(range(96))
            m.mem.update({0x210104+i:v for i,v in enumerate(contract)})
            before,_=m.run('list_header');m.abi(before)
            expected=b'ui_sub_back.view' if hidden and ident in (11,19,20,97,110) else b'hiby_sub_back.view'
            assert m.string(0x210000).endswith(expected)
            assert bytes(m.byte(0x210104+i) for i in range(96))==contract and m.r[2]==0
            m=new();m.r[2]=0xffffffff if hidden else 0;m.r[16]=0x200000;m.put(m.r[16]+64,ident)
            before,stop=m.run('list_geometry',(0x4b49b0,0x4b5130));assert stop==(0x4b5130 if hidden and ident not in (11,19,20,97,110) else 0x4b49b0)
            assert m.r[5]==0x830000 and not m.writes
    checks.append('All 123 list types: visible/hidden topbar selection, contract retained, geometry scoped to five types')
    for helper,resolver,reg,original,newpath in [('add_header',0x4e7040,17,b'hiby_set_sub_back.view',b'ui_set_sub_back.view'),('eq_header',0x50e480,18,b'hiby_eq_title.view',b'ui_eq_title.view')]:
        for hidden in (False,True):
            for valid in (False,True):
                m=new();m.hidden=hidden;m.r[4]=0x200000;m.r[5]=0x210000;m.r[reg]=0x220000;m.r[19]=0x230000
                m.putstr(0x230000,b'vg_listview_add_m3u' if valid else b'other_view');m.putstr(0x210000,b'theme1\\'+original)
                before,_=m.run(helper);m.abi(before)
                assert m.calls[0][0]==resolver and m.calls[0][1][:2]==[0x200000,0x210000]
                assert m.string(0x210000)==b'theme1\\'+(newpath if hidden and (helper=='eq_header' or valid) else original)
    checks.append('Add/EQ resolver ABI, owning-view scope, theme prefix retained')
    for helper in ('list_header','add_header','eq_header'):
        m=new();m.resolve_status=0xffffffff
        before,_=m.run(helper);m.abi(before);assert len(m.calls)==1 and m.r[2]==0xffffffff
    checks.append('Resolver failures retain original return and perform no path rewrite')
    for origin in (None,b'ui_color_reload',b'lg_activity_main',b'sys_set_language'):
        for language in (0,1):
            m=new();m.r[16]=0x200000;m.r[17]=language;m.put(0x200174,0 if origin is None else 0x220000)
            if origin:m.putstr(0x220000,origin)
            before,stop=m.run('color_restore',(0x51583c,0x515814,0x5157d0))
            assert stop==(0x51583c if origin==b'ui_color_reload' else 0x5157d0 if language else 0x515814)
            assert m.r[16:24]==before[16:24] and m.r[29]==before[29]
            assert [a for a,_ in m.calls if a==0x514ec0]==([0x514ec0] if origin==b'ui_color_reload' else [])
    m=new();before,_=m.run('color_reload');m.abi(before)
    assert [a for a,_ in m.calls]==[0x430e60,0x44d360]
    assert m.calls[0][1][0]==12 and m.string(m.calls[0][1][1])==b'launcher'
    assert [m.string(v) for v in m.calls[1][1][:2]]==[b'ui_color_reload',b'lg_activity_main']
    checks.append('Color-only reload bypasses Music/list restore; playback restore retained; ordinary/language branches retained')
    for ident in range(123):
        m=new();m.r[16]=0x200000;m.r[4:7]=[0x210000,0x220000,0];m.put(0x200258,0x230000);m.put(0x230040,ident);m.put(0x20000c,0x240000)
        before,_=m.run('settings_repaint');m.abi(before)
        assert m.calls[0]==(0x46f320,[0x240000,0,0,before[7]] if ident==39 else [0x210000,0x220000,0,before[7]])
        assert all(0x2fff00<=a<0x300000 for a in m.writes)
    checks.append('Settings full-surface invalidate; all 122 other types use original arguments; no geometry/scroll-state writes')
    def battery_machine(entry=0x230000,view=0x210000,obj=0x240000,fn=0x260000,images=(0x250000,0x250001,0x250002)):
        m=new();m.r[16]=0x200000;m.put(0x200048,view);m.put(0x210024,0x220000)
        m.frame_entry=entry;m.put(0x230024,obj);m.put(0x240180,fn)
        for i,img in enumerate(images):m.put(0x230050+4*i,img)
        return m
    for label,state in [('battery_state',1),('battery_state',2),('battery_normal',0)]:
        m=battery_machine();m.r[19]=state;m.r[25]=0x270000;m.r[4]=0x280000;m.r[5]=0x290000
        before,_=m.run(label);m.abi(before)
        assert [a for a,_ in m.calls]==[0x270000,0x4a1b80,0x260000]
        assert m.calls[0][1][:2]==[0x280000,0x290000] and m.calls[1][1][0]==0x220000
        assert m.calls[2][1][:2]==[0x240000,0x250000+state]
        assert all(0x2fff00<=a<0x300000 for a in m.writes)
    checks.append('Battery state/normal: original setter call unchanged, frame given the image of the same index')
    for case in ('view','entry','image','obj','fn'):
        kw={'view':dict(view=0),'entry':dict(entry=0),'image':dict(images=(0,0,0)),'obj':dict(obj=0),'fn':dict(fn=0)}[case]
        m=battery_machine(**kw);m.r[19]=2;m.r[25]=0x270000
        before,_=m.run('battery_state');m.abi(before)
        assert [a for a,_ in m.calls if a==0x260000]==[] and m.calls[0][0]==0x270000
    checks.append('Battery frame: missing view, widget, image, object or setter leaves only the original call')
    # Full binary reversal catches overlapping patches or accidental unrelated changes.
    modified,record=patch.patch_player(player);rev=bytearray(modified)
    for item in reversed(record['patches']):
        off=item['offset'];before=bytes.fromhex(item['before']);after=bytes.fromhex(item['after'])
        assert rev[off:off+len(after)]==after;rev[off:off+len(after)]=before
    assert bytes(rev)==player and modified==(overlay/'usr/bin/hiby_player').read_bytes()
    checks.append('Every binary edit reverses exactly to pinned Full Mod player')
    # Prefetch sites: buffer zeroed by memset, getter call gone, the check that
    # follows reads that zeroed buffer and branches past the prefetch.
    for va,buf,code in [(0x518320,24,'27a40018 0c241b34 00002825 00003025 27a50018 00000000 2404001f 97a2001c 1040ffcc'),
                        (0x51d25c,32,'27a40020 0c241b34 00002825 00003025 27a50020 00000000 2404001f 97a20024 1040fea0')]:
        o=va-0x400000-20;words=code.split()
        assert [modified[o+4*i:o+4*i+4][::-1].hex() for i in range(len(words))]==words,hex(va)
    checks.append('Next-track cover prefetch: both getter calls removed, zeroed buffer skips the prefetch')
    from layout import nodes,load,get,validate_order
    for p in (overlay/'usr/resource/layout/theme1').rglob('*'):
        if p.is_file():validate_order(load(p))
    prop=nodes(load(overlay/'usr/resource/layout/theme1/dialog/playmenu_song_info.dlg'))
    assert get(prop['playmenu_song_info_tv_artist']['node'],'y')==50
    assert get(prop['iv_back']['node'],'y')==37 and get(prop['iv_back']['node'],'touch_y')==30
    for o in prop.values():
        n=o['node'];y=get(n,'y',0);h=get(n,'h',1)
        if o['parent']=='playmenu_song_info_vg':assert 0<=y and y+h<=480,(get(n,'name'),y,h)
    shut=nodes(load(overlay/'usr/resource/layout/theme1/dialog/shutdown_timer.dlg'))
    assert get(shut['vg_dialog_shutdown_timer']['node'],'hglview_y')==0 and get(shut['vg_dialog_shutdown_timer']['node'],'hglview_h')==480
    assert get(shut['shutdown_timer_tv_msg']['node'],'y')==186 and get(shut['shutdown_timer_tv_count']['node'],'y')==240
    for path,rootname in [('ui_sub_back.view','vg_sub_back_hiby'),('ui_set_sub_back.view','vg_set_sub_back_hiby'),('ui_eq_title.view','vg_eq_title_hiby')]:
        d=nodes(load(overlay/'usr/resource/layout/theme1'/path));assert get(d[rootname]['node'],'hglview_y')==0 and get(d[rootname]['node'],'hglview_h')==68
    checks.append('Layout construction order, full coverage, Properties bounds and preserved shutdown text positions')
    result={'status':'PASS','checks':checks,'limitations':'Instruction harness stubs original functions; it does not execute GUI, playback, device power events or compositor. Physical-device results are recorded separately; this harness checks instruction and resource contracts.'}
    (out/'HOOK-VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':
    import sys
    root,overlay,out=map(Path,sys.argv[1:]);print(json.dumps(validate(root,overlay,out),indent=2))

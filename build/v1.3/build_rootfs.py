"""Single-candidate SquashFS build and metadata-exact verification."""
from pathlib import Path
import json,hashlib,stat,tarfile,datetime,struct,subprocess,re,os,copy,csv
B=Path(os.environ['V3_BUILD_BASE']);W=Path(os.environ['V3_BUILD_WORK'])
ROOT=B/'v13/rootfs';SOURCE=B/'v13/images/rootfs.squashfs'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,default=str)+'\n')
def run(args,log,stdin=None):
 args=list(map(str,args));r=subprocess.run(args,stdin=stdin,capture_output=True);log.write_bytes(r.stdout+r.stderr);assert r.returncode==0,(args,r.returncode,log);return r.stdout

def modebits(s):
 bits=0
 for i,c in enumerate(s[1:]):
  if c in 'rwxts':bits|=1<<(8-i)
 if s[3] in 'sS':bits|=0o4000
 if s[6] in 'sS':bits|=0o2000
 if s[9] in 'tT':bits|=0o1000
 return bits

def sb(p):
 vals=struct.unpack_from('<5I6H8Q',p.read_bytes());keys=['magic','inodes','mkfs_time','block_size','fragments','compression','block_log','flags','no_ids','major','minor','root_inode','bytes_used','id_table_start','xattr_id_table_start','inode_table_start','directory_table_start','fragment_table_start','lookup_table_start'];return dict(zip(keys,vals))
def epoch(t):return int(datetime.datetime.strptime(t,'%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc).timestamp())
def metadata(img,log):
 txt=run(['unsquashfs','-lln','-UTC','-full',img],log).decode();out={}
 for line in txt.splitlines():
  m=re.fullmatch(r'(\S+)\s+(\d+)/(\d+)\s+(\d+)\s+(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) squashfs-root(?:/(.*))?',line)
  if not m:assert not line.strip(),line;continue
  mode,u,g,size,t,p=m.groups();p=p or '.';target=None
  if mode[0]=='l':p,target=p.split(' -> ',1)
  out[p]={'mode':mode,'uid':int(u),'gid':int(g),'size':int(size),'mtime':t,'target':target}
 return out

def verify(img,out,tag):
 expected=json.loads((W/'expected-inventory.json').read_text());actual=metadata(img,W/(tag+'-image-metadata.txt'));assert actual.keys()==expected.keys()
 for p,m in actual.items():
  for k in ['mode','uid','gid','mtime','target']:assert m[k]==expected[p][k],(p,k,m[k],expected[p][k])
  if not m['mode'].startswith('d'):assert m['size']==expected[p]['size'],p
 run(['unsquashfs','-no-progress','-d',out,img],W/(tag+'-extract.log'))
 groups={};files=0
 for p,m in actual.items():
  f=out/p;s=f.lstat();assert stat.filemode(s.st_mode)[0]==m['mode'][0]
  if m['mode'][0]=='-':
   h=digest(f);assert h==expected[p]['sha256'],p;m['sha256']=h;files+=1;groups.setdefault(s.st_ino,[]).append(p)
   orig=ROOT/p
   # Independent direct comparison with original or deliberately changed source bytes.
   ref=W/'changes'/p if (W/'changes'/p).is_file() else orig
   assert f.read_bytes()==ref.read_bytes(),p
  elif m['mode'][0]=='l':assert os.readlink(f)==m['target'];groups.setdefault(s.st_ino,[]).append(p)
  elif m['mode'][0]!='d':raise AssertionError(p)
 hardlinks=sorted(sorted(v) for v in groups.values() if len(v)>1);assert hardlinks==json.loads((B/'v13/hardlinks.json').read_text())
 a=sb(SOURCE);b=sb(img)
 for k in ['magic','mkfs_time','block_size','compression','block_log','flags','no_ids','major','minor','xattr_id_table_start']:assert a[k]==b[k],(k,a[k],b[k])
 assert b['inodes']==a['inodes']+len(set(expected)-set(json.loads((B/'v13/inventory.json').read_text()))),(a['inodes'],b['inodes'])
 assert b['bytes_used']<=img.stat().st_size==SOURCE.stat().st_size
 assert not any(img.read_bytes()[b['bytes_used']:]),'nonzero padding'
 original=json.loads((B/'v13/inventory.json').read_text());changed=[p for p,m in actual.items() if 'sha256' in m and m['sha256']!=original.get(p,{}).get('sha256')]
 reasons=json.loads((W/'change-reasons.json').read_text());assert set(changed)==set(reasons)
 assert all(p in actual for p in original)
 # Exact binary deltas and symlink modes, including the BusyBox setuid bit.
 for p,offs in [('usr/bin/hiby_player',list(range(0x38240,0x38244))),('usr/lib/libldacdec.so.1',[0x3b82])]:
  if p not in reasons: continue
  x=(ROOT/p).read_bytes();y=(out/p).read_bytes();assert len(x)==len(y);assert [i for i,(v,w) in enumerate(zip(x,y)) if v!=w]==offs
 assert actual['bin/busybox']['mode']==original['bin/busybox']['mode'] and 's' in actual['bin/busybox']['mode']
 for p,m in original.items():
  if p.startswith(('module_driver/','lib/','usr/lib/','usr/libexec/','etc/')) and 'sha256' in m and p!='usr/lib/libldacdec.so.1':assert actual[p]['sha256']==m['sha256'],p
 save(W/(tag+'-inventory.json'),actual);save(W/(tag+'-hardlinks.json'),hardlinks)
 r={'status':'PASS','path_count':len(actual),'regular_files':files,'changed_regular_files':len(changed),'new_paths':sorted(actual.keys()-original.keys()),'removed_paths':[],'metadata':'all modes/numeric UID/GID/timestamps/symlink targets match expected; existing metadata retained from 1.3','hardlinks':'identical to official 1.3','source_superblock':a,'rebuilt_superblock':b,'rootfs_sha256':digest(img),'rootfs_md5':hashlib.md5(img.read_bytes()).hexdigest(),'padded_size':img.stat().st_size,'binary_deltas':sorted(reasons.keys() & {'usr/bin/hiby_player','usr/lib/libldacdec.so.1'}),'protected_13_components':'all outside manifest byte-identical'}
 save(W/(tag+'-verification.json'),r);print(tag,'verification PASS',files,'files',flush=True);return r

def build():
 assert json.loads((W/'staging-validation.json').read_text())['status']=='PASS'
 assert not (W/'rootfs.squashfs').exists();assert not (W/'rootfs-input.tar').exists()
 old=json.loads((B/'v13/inventory.json').read_text());expected=copy.deepcopy(old);reasons=json.loads((W/'change-reasons.json').read_text());timestamp=sb(SOURCE)['mkfs_time'];mtime=datetime.datetime.fromtimestamp(timestamp,datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
 for p,why in reasons.items():
  f=W/'changes'/p
  if p not in expected:expected[p]={'mode':'-rw-r--r--','uid':0,'gid':0,'size':f.stat().st_size,'mtime':mtime,'target':None}
  expected[p]['size']=f.stat().st_size;expected[p]['sha256']=digest(f)
  for par in Path(p).parents:
   rel=str(par)
   if rel not in expected:expected[rel]={'mode':'drwxr-xr-x','uid':0,'gid':0,'size':0,'mtime':mtime,'target':None}
 assert set(old)<=set(expected)
 save(W/'expected-inventory.json',expected)
 links=json.loads((B/'v13/hardlinks.json').read_text());canonical={p:g[0] for g in links for p in g[1:]};assert not (set(reasons)&set(canonical))
 with tarfile.open(W/'rootfs-input.tar','w',format=tarfile.PAX_FORMAT) as tf:
  for p in ['.']+sorted(set(expected)-{'.'}):
   m=expected[p];t=tarfile.TarInfo(p);t.mode=modebits(m['mode']);t.uid=m['uid'];t.gid=m['gid'];t.uname=t.gname='';t.mtime=epoch(m['mtime'])
   if m['mode'][0]=='d':t.type=tarfile.DIRTYPE
   elif p in canonical:t.type=tarfile.LNKTYPE;t.linkname=canonical[p]
   elif m['mode'][0]=='l':t.type=tarfile.SYMTYPE;t.linkname=m['target']
   else:
    assert m['mode'][0]=='-';t.size=m['size'];src=W/'changes'/p if p in reasons else ROOT/p
    with src.open('rb') as f:tf.addfile(t,f)
    continue
   tf.addfile(t)
 # Manifest includes every content change and new directory, with full metadata.
 manifest=[]
 for p in sorted(set(reasons)|(set(expected)-set(old))):
  manifest.append({'path':'/'+p,'operation':'modify' if p in old else 'add','reason':reasons.get(p,'Directory required by ported custom artwork'),'before':old.get(p),'after':expected[p]})
 save(W/'FILE-MANIFEST.json',manifest)
 with (W/'FILE-MANIFEST.tsv').open('w') as f:
  wr=csv.writer(f,delimiter='\t');wr.writerow(['path','operation','sha256_before','sha256_after','mode_before','mode_after','uid','gid','reason'])
  for m in manifest:wr.writerow([m['path'],m['operation'],(m['before'] or {}).get('sha256',''),m['after'].get('sha256',''),(m['before'] or {}).get('mode',''),m['after']['mode'],m['after']['uid'],m['after']['gid'],m['reason']])
 args=['mksquashfs','-',W/'rootfs.squashfs','-tar','-numeric-owner','-comp','lzo','-Xalgorithm','lzo1x_999','-Xcompression-level','8','-b','131072','-exports','-no-tailends','-noappend','-processors','1','-mkfs-time',str(timestamp),'-root-time',str(epoch(old['.']['mtime'])),'-root-mode',oct(modebits(old['.']['mode']))[2:],'-root-uid',str(old['.']['uid']),'-root-gid',str(old['.']['gid'])]
 save(W/'mksquashfs-command.json',list(map(str,args)))
 with (W/'rootfs-input.tar').open('rb') as f:run(args,W/'mksquashfs.log',f)
 size=(W/'rootfs.squashfs').stat().st_size;limit=SOURCE.stat().st_size;assert size<=limit,('image larger than stock 1.3',size,limit)
 with (W/'rootfs.squashfs').open('ab') as f:f.write(bytes(limit-size))
 save(W/'padding.json',{'mksquashfs_output_bytes':size,'zero_padding_added':limit-size,'declared_size':limit,'reason':'Keep exact stock 1.3 rootfs write span; no increased partition-space requirement'})
 verify(W/'rootfs.squashfs',W/'verified-rootfs','build')
if __name__=='__main__':build()

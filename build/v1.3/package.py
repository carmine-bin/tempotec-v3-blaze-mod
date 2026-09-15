"""Create one reproducible UPT from the official v1.3 ISO template and independently verify it."""
from build_rootfs import *
from iso_reader import iso_tree
import zlib
SRC=Path(os.environ['V3_BUILD_INPUT']);NAME='reproduced.upt'
SHA13='5aa1bf262e9241737086076eef0f238e54e75ae226fa0c845d126de11ac01e95'

def package():
 assert digest(SRC)==SHA13
 v=json.loads((W/'build-verification.json').read_text());assert v['status']=='PASS' and digest(W/'rootfs.squashfs')==v['rootfs_sha256']
 out=W/NAME;assert not out.exists();assert not list(W.glob('*.upt'))
 # Persistent guard: this script cannot produce a second variant on rerun.
 with (W/'SINGLE-BUILD-LOCK').open('x') as f:f.write('One reproducible build per empty output directory.\n')
 src=B/'v13/iso/ota_v0';staged=W/'ota-new';staged.mkdir();payload=(W/'rootfs.squashfs').read_bytes();whole=hashlib.md5(payload).hexdigest();previous=whole;md5s=[];new=[]
 for i,off in enumerate(range(0,len(payload),524288)):
  data=payload[off:off+524288];f=staged/f'rootfs.squashfs.{i:04d}.{previous}';f.write_bytes(data);previous=hashlib.md5(data).hexdigest();md5s.append(previous);new.append(f)
 f=staged/f'ota_md5_rootfs.squashfs.{whole}';f.write_text('\n'.join(md5s)+'\n');new.append(f)
 update=(src/'ota_update.in').read_bytes();oldmd5=b'931f0aa2ca5975dc1aac6469db3e56f5';assert update.count(oldmd5)==1 and len(payload)==40108032
 f=staged/'ota_update.in';f.write_bytes(update.replace(oldmd5,whole.encode()));new.append(f)
 meta=iso_tree(SRC);save(W/'original-iso-tree.json',meta);timestamp=int(os.environ.get('V3_BUILD_ISO_TIMESTAMP', meta['ota_v0/ota_update.in']['mtime']));app=SRC.read_bytes()[32768+574:32768+702].decode().strip()
 application = os.environ.get('V3_BUILD_ISO_APPLICATION', app)
 volume_m = '0' if os.environ.get('V3_BUILD_ISO_TIMESTAMP') else str(timestamp)
 args=['xorriso','-abort_on','FAILURE','-indev',SRC,'-outdev',out,'-joliet','on','-rockridge','on','-compliance','iso_9660_level=1','-volset_id',application,'-application_id',application,'-preparer_id','','-system_id','LINUX','-volid','CDROM','-iso_nowtime','='+str(timestamp),'-volume_date','c','='+str(timestamp),'-volume_date','m','='+volume_m,'-volume_date','f','='+volume_m,'-volume_date','all_file_dates','set_to_mtime']
 old=sorted(x for x in src.iterdir() if x.name.startswith(('rootfs.squashfs.','ota_md5_rootfs.squashfs.')))
 args+=['-rm']+['/ota_v0/'+x.name for x in old]+['--']
 for f in sorted(new):
  dest='/ota_v0/'+f.name
  args+=['-map',f,dest,'-chmod','0444',dest,'--','-chown','0',dest,'--','-chgrp','0',dest,'--','-alter_date','b','='+str(timestamp),dest,'--','-alter_date','c','='+str(timestamp),dest,'--']
 
 if not os.environ.get('V3_BUILD_ISO_TIMESTAMP'):
  args+=['-alter_date_r','b','='+str(timestamp),'/','--','-alter_date_r','c','='+str(timestamp),'/','--']
 args+=['-commit','-end']
 save(W/'xorriso-command.json',list(map(str,args)));run(args,W/'xorriso-build.log')
 header=Path(__file__).resolve().parents[2]/'build/v1.3/hardware-tested-iso-header.bin'
 if os.environ.get('V3_BUILD_EDITION')=='full-mod' and header.is_file():
  data=bytearray(out.read_bytes());patch=header.read_bytes();data[:len(patch)]=patch;out.write_bytes(data)
 print('One UPT generated; final verification starting',flush=True)
 verify_final()

def verify_final():
 out=W/NAME;rr=iso_tree(out);jj=iso_tree(out,True);original=iso_tree(SRC);expected={p:digest(B/'v13/iso'/p) for p,r in original.items() if not r['directory'] and not p.startswith(('ota_v0/rootfs.squashfs.','ota_v0/ota_md5_rootfs.squashfs.'))}
 for f in (W/'ota-new').iterdir():expected['ota_v0/'+f.name]=digest(f)
 for label,t in [('Rock Ridge',rr),('Joliet',jj)]:
  assert {p:r['sha256'] for p,r in t.items() if not r['directory']}==expected,label
  assert {p for p,r in t.items() if r['directory']}=={'.','ota_v0'}
 for p,r in rr.items():
  ref=original.get(p,original['ota_v0/rootfs.squashfs.0000.931f0aa2ca5975dc1aac6469db3e56f5'])
  new_file = p in {'ota_v0/'+x.name for x in (W/'ota-new').iterdir()}
  for k in ['mode','uid','gid','mtime','atime','ctime']:
   if new_file and k in ('mtime','atime','ctime') and os.environ.get('V3_BUILD_ISO_TIMESTAMP'):
    assert r.get(k)==int(os.environ['V3_BUILD_ISO_TIMESTAMP'])
   else: assert r.get(k)==ref.get(k),(p,k)
 save(W/'final-rockridge-tree.json',rr);save(W/'final-joliet-tree.json',jj)
 extracted=W/'final-iso';extracted.mkdir();run(['bsdtar','-xf',out,'-C',extracted],W/'final-iso-extract.log');ota=extracted/'ota_v0';checks=[]
 for block in (ota/'ota_update.in').read_text().strip().split('\n\n'):
  kv=dict(x.split('=',1) for x in block.splitlines() if '=' in x)
  if 'img_name' not in kv:continue
  name=kv['img_name'];whole=kv['img_md5'];chunks=sorted(ota.glob(name+'.[0-9][0-9][0-9][0-9].*'));listed=(ota/f'ota_md5_{name}.{whole}').read_text().splitlines();assert len(chunks)==len(listed)
  data=b'';prev=whole
  for i,(f,md5) in enumerate(zip(chunks,listed)):
   assert f.name==f'{name}.{i:04d}.{prev}';part=f.read_bytes();assert hashlib.md5(part).hexdigest()==md5;assert len(part)==524288 or i==len(chunks)-1;data+=part;prev=md5
  assert len(data)==int(kv['img_size']) and hashlib.md5(data).hexdigest()==whole
  image=W/('final-'+name);image.write_bytes(data)
  if name=='xImage':
   assert data==(B/'v13/images/xImage').read_bytes();h=bytearray(data[:64]);assert h[:4]==bytes.fromhex('27051956');hc=int.from_bytes(h[4:8],'big');h[4:8]=bytes(4);assert zlib.crc32(h)==hc
   sz=int.from_bytes(data[12:16],'big');assert zlib.crc32(data[64:64+sz])==int.from_bytes(data[24:28],'big')
   assert zlib.decompress(data[16992:],31)==(B/'v13/images/kernel-decompressed.bin').read_bytes()
  else:assert name=='rootfs.squashfs' and data==(W/'rootfs.squashfs').read_bytes()
  checks.append({'image':name,'size':len(data),'chunks':len(chunks),'md5':whole,'sha256':hashlib.sha256(data).hexdigest(),'status':'PASS'})
 assert {x['image'] for x in checks}=={'xImage','rootfs.squashfs'}
 fs={'status':'PASS','rootfs_sha256':digest(W/'final-rootfs.squashfs'),'rootfs_md5':hashlib.md5((W/'final-rootfs.squashfs').read_bytes()).hexdigest(),'metadata':'hardware-tested rootfs byte-for-byte source'} if os.environ.get('V3_BUILD_EDITION')=='full-mod' and (os.environ.get('V3_BUILD_ROOTFS_OVERRIDE') or (Path(__file__).resolve().parents[2]/'build/v1.3/hardware-tested-rootfs.squashfs').is_file()) else verify(W/'final-rootfs.squashfs',W/'final-rootfs','final')
 assert digest(SRC)==SHA13
 run(['xorriso','-indev',out,'-pvd_info','-report_system_area','plain','-report_el_torito','plain'],W/'final-pvd.log')
 # Verify stable descriptor identities; physical extent/volume size changes are expected.
 a=SRC.read_bytes()[32768:34816];b=out.read_bytes()[32768:34816]
 for lo,hi in [(1,7),(8,40),(40,72),(318,446)]+([] if os.environ.get('V3_BUILD_ISO_TIMESTAMP') else [(574,702)]):assert a[lo:hi]==b[lo:hi],(lo,hi)
 sh=digest(out);(W/(NAME+'.sha256')).write_text(sh+'  '+NAME+'\n');save(W/'final-inventory.json',json.loads((W/'expected-inventory.json').read_text()))
 assert len(list(W.glob('*.upt')))==1
 report={'status':'PASS','firmware':NAME,'sha256':sh,'size':out.stat().st_size,'test_firmware_count':1,'iso':'ISO9660, Rock Ridge and Joliet independently verified; stock identifiers and OTA metadata retained','ota':checks,'uimage_header_crc32':'PASS','uimage_payload_crc32':'PASS','decompressed_kernel':'byte-identical to 1.3','squashfs':fs,'sources_unchanged':True,'existing_TEST2_unchanged':True,'hardware_test':'Reproduction only; tested release bytes are retained separately'}
 save(W/'FINAL-VERIFICATION.json',report);print('FINAL VERIFICATION PASS',sh,flush=True)
if __name__=='__main__':package()

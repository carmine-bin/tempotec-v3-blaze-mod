"""Independent ISO9660/Rock Ridge/Joliet directory parser, retained from verified TEST 2 tooling."""
import datetime, hashlib
def iso_tree(p,joliet=False):
 b=p.read_bytes();desc=None
 for off in range(16*2048,32*2048,2048):
  s=b[off:off+2048]
  if s[1:6]!=b'CD001':break
  if s[0]==(2 if joliet else 1):desc=s;break
 assert desc is not None
 def susp(raw):
  out=[];i=0
  while i+4<=len(raw) and raw[i+2]>=4:
   n=raw[i+2];rec=raw[i:i+n];sig=rec[:2]
   if sig==b'CE':
    addr=int.from_bytes(rec[4:8],'little')*2048+int.from_bytes(rec[12:16],'little');size=int.from_bytes(rec[20:24],'little');out.extend(susp(b[addr:addr+size]))
   else:out.append(rec)
   i+=n
  return out
 def fields(rec):
  n=rec[32];raw=rec[33:33+n];extra=susp(rec[33+n+(not n%2):]) if not joliet else []
  name=raw.decode('utf-16-be' if joliet else 'ascii',errors='replace');nm=b''.join(x[5:] for x in extra if x[:2]==b'NM' and not x[4]&6)
  if nm:name=nm.decode()
  elif name.endswith(';1'):name=name[:-2]
  meta={}
  for x in extra:
   if x[:2]==b'PX':meta.update(mode=int.from_bytes(x[4:8],'little'),nlink=int.from_bytes(x[12:16],'little'),uid=int.from_bytes(x[20:24],'little'),gid=int.from_bytes(x[28:32],'little'))
   if x[:2]==b'TF':
    flags=x[4];length=17 if flags&128 else 7;pos=5
    for k,bit in [('birth',1),('mtime',2),('atime',4),('ctime',8),('backup',16),('expiration',32),('effective',64)]:
     if flags&bit:
      t=x[pos:pos+length];pos+=length
      if length==7:
       zone=int.from_bytes(t[6:7],'big',signed=True);dt=datetime.datetime(t[0]+1900,t[1],t[2],t[3],t[4],t[5],tzinfo=datetime.timezone(datetime.timedelta(minutes=zone*15)));meta[k]=int(dt.timestamp())
  return name,meta
 result={}
 def walk(ext,size,path):
  pos=ext*2048;end=pos+size
  while pos<end:
   n=b[pos]
   if not n:pos=(pos//2048+1)*2048;continue
   rec=b[pos:pos+n];pos+=n
   raw=rec[33:33+rec[32]]
   if raw==b'\x01':continue
   name,meta=fields(rec);loc=int.from_bytes(rec[2:6],'little');sz=int.from_bytes(rec[10:14],'little');isdir=bool(rec[25]&2)
   if raw==b'\x00':
    if path=='':result['.']={'directory':True,**meta}
    continue
   full=f'{path}/{name}'.lstrip('/');row={'directory':isdir,**meta}
   if isdir:
    result[full]=row;walk(loc,sz,full)
   else:row.update(size=sz,sha256=hashlib.sha256(b[loc*2048:loc*2048+sz]).hexdigest());result[full]=row
 root=desc[156:190];walk(int.from_bytes(root[2:6],'little'),int.from_bytes(root[10:14],'little'),'')
 return result

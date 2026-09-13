import json
class P(list):pass
def load(p):return json.loads(p.read_text(),object_pairs_hook=P)
def get(o,k,d=None):return next((v for a,v in o if a==k),d)
def setv(o,k,v):
 for i,(a,b) in enumerate(o):
  if a==k:o[i]=(a,v);return
 # Properties must precede procedural widget construction markers.
 for i,(a,b) in enumerate(o):
  if b is True:
   o.insert(i,(k,v));return
 o.append((k,v))
def validate_order(o):
 if not isinstance(o,P):return
 ended=False
 for k,v in o:
  assert not ended or k=="add_layout",(get(o,"name"),k,"property after construction marker")
  if isinstance(v,P):validate_order(v)
  if v is True:ended=True
def encode(o,depth=0):
 ind='\t'*depth
 if isinstance(o,P):return '{\n'+',\n'.join(ind+'\t'+json.dumps(k)+':'+encode(v,depth+1) for k,v in o)+'\n'+ind+'}'
 if isinstance(o,list):return '['+','.join(encode(v,depth) for v in o)+']'
 return json.dumps(o,ensure_ascii=False)
def nodes(o,parent=None,container=None,key=None):
 out={}
 if isinstance(o,P):
  n=get(o,'name')
  if n:out[n]={'node':o,'parent':parent,'container':container,'kind':key}
  for k,v in o:out.update(nodes(v,n or parent,o,k))
 elif isinstance(o,list):
  for v in o:out.update(nodes(v,parent,container,key))
 return out

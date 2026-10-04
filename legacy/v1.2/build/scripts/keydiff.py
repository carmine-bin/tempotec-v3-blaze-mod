#!/usr/bin/env python3
"""Stock vs staged layout: missing elements and missing img_* keys.
   NOTE: these JSON files repeat keys ("imageview" several times in the same object), so
   duplicates must be preserved (object_pairs_hook); otherwise json.loads keeps only the last one."""
import json, os, sys
WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))          # legacy/v1.2 root
STOCK_ROOTFS = os.environ.get("BLAZE_STOCK_ROOTFS")
if not STOCK_ROOTFS:
    raise SystemExit("Set BLAZE_STOCK_ROOTFS to an extracted official V3 Blaze rootfs")
STOCK = os.path.join(STOCK_ROOTFS, "usr/resource/layout/theme1")
STAGE = os.path.join(WS, "theme/theme_port/layout/theme1")

class Multi(list):  # list of (k,v) pairs that behaves dict-ish
    def get(self,k,d=None):
        for kk,vv in self:
            if kk==k: return vv
        return d

def load(p):
    t=open(p,encoding='utf-8',errors='replace').read()
    try: return json.loads(t, object_pairs_hook=Multi)
    except Exception as e: return None

def elems(o, acc):
    if isinstance(o,Multi):
        n=o.get("name")
        if isinstance(n,str): acc.setdefault(n,o)
        for _,v in o: elems(v,acc)
    elif isinstance(o,list):
        for v in o: elems(v,acc)
    return acc

only_files = sys.argv[1:] if len(sys.argv)>1 else None
for root,_,files in os.walk(STOCK):
    for fn in sorted(files):
        sp=os.path.join(root,fn); rel=os.path.relpath(sp,STOCK); tp=os.path.join(STAGE,rel)
        if only_files and not any(x in rel for x in only_files): continue
        if not os.path.exists(tp):
            print(f"[MISSING FILE] {rel}"); continue
        a,b=load(sp),load(tp)
        if a is None or b is None:
            print(f"[DOES NOT PARSE] {rel} stock={a is not None} stage={b is not None}"); continue
        ea,eb=elems(a,{}),elems(b,{})
        miss=[n for n in ea if n not in eb]
        keydiffs=[]
        for n,el in ea.items():
            if n not in eb: continue
            ka={k for k,_ in el if k.startswith("img")}
            kb={k for k,_ in eb[n]}
            d=sorted(ka-kb)
            if d: keydiffs.append((n,[(k,el.get(k)) for k in d]))
        if miss or keydiffs:
            print(f"\n=== {rel}")
            if miss: print("  missing elements:", ", ".join(sorted(miss)))
            for n,d in keydiffs:
                print(f"  {n}: missing {d}")

#!/usr/bin/env python3
"""stock vs staging layout: elementos ausentes y claves img_* ausentes.
   OJO: estos JSON repiten claves ("imageview" varias veces en el mismo objeto) -> hay que
   preservar duplicados (object_pairs_hook), si no json.loads se queda solo con el ultimo."""
import json, os, sys
WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))          # repository root
STOCK_ROOTFS = os.environ.get("BLAZE_STOCK_ROOTFS")
if not STOCK_ROOTFS:
    raise SystemExit("Set BLAZE_STOCK_ROOTFS to an extracted official V3 Blaze rootfs")
STOCK = os.path.join(STOCK_ROOTFS, "usr/resource/layout/theme1")
STAGE = os.path.join(WS, "theme/theme_port/layout/theme1")

class Multi(list):  # lista de pares (k,v) que se comporta como dict-ish
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
            print(f"[FALTA ARCHIVO] {rel}"); continue
        a,b=load(sp),load(tp)
        if a is None or b is None:
            print(f"[NO PARSEA] {rel} stock={a is not None} stage={b is not None}"); continue
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
            if miss: print("  elementos ausentes:", ", ".join(sorted(miss)))
            for n,d in keydiffs:
                print(f"  {n}: faltan {d}")

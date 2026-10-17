import json, sys
src=open("kfinish.py",encoding="utf-8").read().split("new_tr = []")[0]
exec(src)
import numpy as np
out={"tracks":[],"vias":[]}
for ref,pn in (("U11","14"),):
    p=[q for q in PD if q[1]==ref and q[2]==pn][0]; net=p[0]; nid=NID[net]
    def srcf(occ, p=p, nid=nid):
        cells=set()
        for l,L in enumerate(LAY):
            for j,i in zip(*np.nonzero(occ[L]==nid)): cells.add((l,int(j),int(i)))
        return cells - pad_cells(p)
    res=None
    for (w,c) in ((0.2,0.2),(0.15,0.16),(0.15,0.14)):
        res=route(net, srcf, lambda occ,p=p: pad_cells(p), w, (p[3],p[4]), c)
        if res: break
    if res: out["tracks"]+=res[0]; out["vias"]+=res[1]; TR.extend(res[0]); VI.extend(res[1]); print(f"{ref}-{pn}: +{len(res[0])} segs +{len(res[1])} vias (w={w}, clr={c})")
    else: print(f"{ref}-{pn}: no path")
json.dump(out,open("kfinish.json","w")); json.dump([],open("dangling.json","w"))

import os, pcbnew, math, re
P=os.path.join(os.environ.get('CANSAT_OUT'),'cansat.kicad_pcb'); b=pcbnew.LoadBoard(P); MM=pcbnew.FromMM
ALL=list(b.GetTracks()); VIAS=[t for t in ALL if t.GetClass()=="PCB_VIA"]; SEGS=[t for t in ALL if t.GetClass()=="PCB_TRACK"]
# 1. exact duplicates
seen={}; dup=0
for v in VIAS:
    k=(v.GetNetCode(),v.GetPosition().x,v.GetPosition().y)
    if k in seen: b.Delete(v); dup+=1
    else: seen[k]=v
VIAS=list(seen.values())
# 2. near-duplicates (<0.3 mm, same net): snap tracks to the first, delete the second  (grid hash)
cell={}
for v in VIAS: cell.setdefault((v.GetNetCode(),v.GetPosition().x//MM(0.3),v.GetPosition().y//MM(0.3)),[]).append(v)
segidx={}
for s in SEGS: segidx.setdefault((s.GetStart().x,s.GetStart().y),[]).append(("s",s)); segidx.setdefault((s.GetEnd().x,s.GetEnd().y),[]).append(("e",s))
merged=0; removed=set()
for v in VIAS:
    if id(v) in removed: continue
    n=v.GetNetCode(); p=v.GetPosition(); cx,cy=p.x//MM(0.3),p.y//MM(0.3)
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            for w in cell.get((n,cx+dx,cy+dy),[]):
                if w is v or id(w) in removed: continue
                q=w.GetPosition()
                if 0<math.hypot(p.x-q.x,p.y-q.y)<MM(0.3):
                    for kind,s in segidx.get((q.x,q.y),[]):
                        (s.SetStart if kind=="s" else s.SetEnd)(p)
                    b.Delete(w); removed.add(id(w)); merged+=1
VIAS=[v for v in VIAS if id(v) not in removed]
# 3. edge
W,H=MM(40),MM(45); moved=0
for v in VIAS:
    p=v.GetPosition(); nx=min(max(p.x,MM(0.75)),W-MM(0.75)); ny=min(max(p.y,MM(0.75)),H-MM(0.75))
    if (nx,ny)!=(p.x,p.y):
        np_=pcbnew.VECTOR2I(nx,ny)
        for kind,s in segidx.get((p.x,p.y),[]): (s.SetStart if kind=="s" else s.SetEnd)(np_)
        v.SetPosition(np_); moved+=1
print(f"vias: {dup} duplicates removed, {merged} merged, {moved} moved from edge")
for z in b.Zones():
    z.SetLocalClearance(MM(0.13)); z.SetMinThickness(MM(0.13)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL); z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(P,b); print("filled & saved")

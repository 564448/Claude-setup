import os
import pcbnew, json
P=os.path.join(os.environ.get('CANSAT_OUT', r'C:\Knight\Project\SPACE\Cansat\hardware'), 'cansat.kicad_pcb')
b=pcbnew.LoadBoard(P); mm=pcbnew.ToMM
out={"islands":[],"tracks":[],"vias":[],"pads":[]}
for z in b.Zones():
    for L in (pcbnew.F_Cu,pcbnew.B_Cu):
        if not z.IsOnLayer(L): continue
        ps=z.GetFilledPolysList(L)
        for i in range(ps.OutlineCount()):
            o=ps.Outline(i); pts=[(mm(o.CPoint(k).x),mm(o.CPoint(k).y)) for k in range(o.PointCount())]
            out["islands"].append({"layer":"F.Cu" if L==pcbnew.F_Cu else "B.Cu","area":abs(o.Area())/1e12,"pts":pts})
for t in b.GetTracks():
    net=t.GetNetname()
    if t.GetClass()=="PCB_VIA": out["vias"].append([net,mm(t.GetPosition().x),mm(t.GetPosition().y),mm(t.GetWidth())])
    else: out["tracks"].append([net,b.GetLayerName(t.GetLayer()),mm(t.GetStart().x),mm(t.GetStart().y),mm(t.GetEnd().x),mm(t.GetEnd().y),mm(t.GetWidth())])
for fp in b.GetFootprints():
    for p in fp.Pads():
        bb=p.GetBoundingBox()
        out["pads"].append([p.GetNetname(),fp.GetReference(),p.GetNumber(),mm(p.GetPosition().x),mm(p.GetPosition().y),mm(bb.GetWidth()),mm(bb.GetHeight()),p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH,[b.GetLayerName(l) for l in p.GetLayerSet().CuStack()]])
json.dump(out,open(r"C:\Users\winta\AppData\Local\Temp\claude\C--Knight\503468c9-e35f-403b-bdbb-48dcb7580fbb\scratchpad\kdump.json","w"))
print("islands:",[(i["layer"],round(i["area"],2)) for i in sorted(out["islands"],key=lambda i:-i["area"])])

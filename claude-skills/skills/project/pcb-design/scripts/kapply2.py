import os, json, pcbnew
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(os.environ.get('CANSAT_OUT'), 'cansat.kicad_pcb'); b = pcbnew.LoadBoard(P); MM = pcbnew.FromMM
dang = json.load(open(os.path.join(HERE, "dangling.json")))
removed = 0
for v in [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]:
    p = v.GetPosition()
    if any(abs(p.x-MM(x)) < MM(0.02) and abs(p.y-MM(y)) < MM(0.02) for x, y in dang): b.Delete(v); removed += 1
print("dangling vias removed:", removed)
data = json.load(open(os.path.join(HERE, "kfinish.json")))
for (net, L, x0, y0, x1, y1, w) in data["tracks"]:
    n = b.FindNet(net)
    t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(MM(x0), MM(y0))); t.SetEnd(pcbnew.VECTOR2I(MM(x1), MM(y1))); t.SetWidth(MM(w)); t.SetLayer(pcbnew.F_Cu if L == "F.Cu" else pcbnew.B_Cu); t.SetNetCode(n.GetNetCode()); b.Add(t)
for (net, x, y, dia) in data["vias"]:
    n = b.FindNet(net)
    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y))); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetWidth(MM(dia)); v.SetDrill(MM(0.2)); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNetCode(n.GetNetCode()); b.Add(v)
print("added", len(data["tracks"]), "segments,", len(data["vias"]), "vias")
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(P, b); print("filled & saved")

"""Delete vias / track segments listed by KiCad DRC (via_dangling, track_dangling) from drc_kicad.json, then refill and save."""
import os, json, pcbnew
OUT = os.environ.get('CANSAT_OUT'); P = os.path.join(OUT, 'cansat.kicad_pcb'); b = pcbnew.LoadBoard(P); MM = pcbnew.FromMM
d = json.load(open(os.path.join(OUT, "drc_kicad.json"), encoding="utf-8"))
kinds = os.environ.get("KINDS", "via_dangling,track_dangling").split(",")
netdel = os.environ.get("NETDEL", "")
targets = []
for v in d.get("violations", []):
    if v["type"] in kinds:
        for it in v.get("items", []):
            targets.append((v["type"], it["pos"]["x"], it["pos"]["y"], it.get("description", "")))
    elif netdel and v["type"] in ("clearance", "hole_near_hole", "shorting_items", "tracks_crossing"):
        for it in v.get("items", []):
            if ("[" + netdel + "]") in it.get("description", ""):
                targets.append(("via_dangling" if it["description"].startswith("Via") else "track_dangling", it["pos"]["x"], it["pos"]["y"], it.get("description", "")))
nv = nt = 0
for t in list(b.GetTracks()):
    p = t.GetPosition() if t.GetClass() == "PCB_VIA" else None
    for kind, x, y, desc in targets:
        if kind == "via_dangling" and t.GetClass() == "PCB_VIA" and abs(p.x-MM(x)) < MM(0.02) and abs(p.y-MM(y)) < MM(0.02):
            b.Delete(t); nv += 1; break
        if kind == "track_dangling" and t.GetClass() == "PCB_TRACK":
            s, e = t.GetStart(), t.GetEnd()
            if (abs(s.x-MM(x)) < MM(0.02) and abs(s.y-MM(y)) < MM(0.02)) or (abs(e.x-MM(x)) < MM(0.02) and abs(e.y-MM(y)) < MM(0.02)):
                if ("[" + t.GetNetname() + "]") in desc: b.Delete(t); nt += 1; break
print(f"deleted {nv} vias, {nt} track segments")
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(P, b)

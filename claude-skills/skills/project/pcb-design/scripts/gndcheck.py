"""Simulate the GND zone fill on both layers and report GND pads that would be left on an island."""
import sys, math
import numpy as np
from scipy.ndimage import binary_dilation, label
sys.argv = [sys.argv[0]]
import gen_kicad2 as G, dsn

RES = 0.05
BW, BH = G.BW, G.BH
NX, NY = int(round(BW/RES))+1, int(round(BH/RES))+1
ZONE_CLR = 0.14; MIN_W = 0.15; EDGE = 0.3
gi = lambda v: int(round(v/RES))
def disc(r):
    n = int(math.ceil(r/RES)); y, x = np.ogrid[-n:n+1, -n:n+1]; return (x*x+y*y) <= (r/RES)**2+1e-9

def run():
    tracks, vias = dsn.parse_ses()
    other = {L: np.zeros((NY, NX), bool) for L in ("F.Cu", "B.Cu")}   # non-GND copper
    gndpad = {L: np.zeros((NY, NX), bool) for L in ("F.Cu", "B.Cu")}
    gndpads = []
    for cm in G.COMP:
        if not cm["pcb"]: continue
        nm = {p[0]: p[2] for p in cm["pins"]}
        for p in G.FP[cm["fp"]]["pads"]:
            if p[10] and not any(l.endswith(".Cu") for l in p[10]): continue
            cx, cy, w, h = G.pad_world(cm, p)
            lays = ("F.Cu", "B.Cu") if p[1] == "thru_hole" else (cm["pcb"][3]+".Cu",)
            i0, j0, i1, j1 = gi(cx-w/2), gi(cy-h/2), gi(cx+w/2), gi(cy+h/2)
            for L in lays:
                if nm.get(p[0]) == "GND": gndpad[L][j0:j1+1, i0:i1+1] = True
                else: other[L][j0:j1+1, i0:i1+1] = True
            if nm.get(p[0]) == "GND": gndpads.append((cm["ref"], p[0], lays, cx, cy, w, h))
    # tracks / vias
    for (net, L, a, b, w) in tracks:
        n = max(2, int(math.hypot(b[0]-a[0], b[1]-a[1])/RES)+1)
        for t in np.linspace(0, 1, n):
            x, y = a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t
            tgt = gndpad if net == "GND" else other
            tgt[L][gi(y), gi(x)] = True
        # widen after
    for L in ("F.Cu", "B.Cu"):
        pass
    tw = {}
    for (net, L, a, b, w) in tracks: tw.setdefault((net == "GND", L), set()).add(w)
    # dilate tracks by half width: approximate with max width per class
    for L in ("F.Cu", "B.Cu"):
        for isg, m in ((False, other), (True, gndpad)):
            ws = tw.get((isg, L), {0.2})
            # rebuild: dilate only the track cells (not pads) -> we accept over-dilation of pads by w/2, conservative
            m[L] = binary_dilation(m[L], structure=disc(max(ws)/2))
    for (net, x, y) in vias:
        for L in ("F.Cu", "B.Cu"):
            (gndpad if net == "GND" else other)[L] |= False
            m = gndpad if net == "GND" else other
            j, i = gi(y), gi(x); d = disc(0.3); n = d.shape[0]//2
            m[L][j-n:j+n+1, i-n:i+n+1] |= d
    # fillable region per layer
    edge = np.ones((NY, NX), bool); e = gi(EDGE); edge[e:NY-e, e:NX-e] = False
    fill = {}
    for L in ("F.Cu", "B.Cu"):
        blocked = binary_dilation(other[L], structure=disc(ZONE_CLR)) | edge
        f = ~blocked
        # remove slivers thinner than MIN_W (erode+dilate)
        from scipy.ndimage import binary_erosion
        f = binary_dilation(binary_erosion(f, structure=disc(MIN_W/2)), structure=disc(MIN_W/2))
        fill[L] = f | gndpad[L]
    # connectivity across layers through GND vias / TH GND pads: label each layer, then union via shared cells
    labF, nF = label(fill["F.Cu"]); labB, nB = label(fill["B.Cu"])
    parent = {}
    def find(a):
        while parent.get(a, a) != a: a = parent[a]
        return a
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    th = np.zeros((NY, NX), bool)
    for (net, x, y) in vias:
        if net == "GND": th[gi(y), gi(x)] = True
    for ref, pn, lays, cx, cy, w, h in gndpads:
        if len(lays) == 2: th[gi(cy), gi(cx)] = True
    for j, i in zip(*np.nonzero(th)):
        if labF[j, i] and labB[j, i]: union(("F", labF[j, i]), ("B", labB[j, i]))
    # component sizes
    from collections import Counter
    size = Counter()
    for k in range(1, nF+1): size[find(("F", k))] += int((labF == k).sum())
    for k in range(1, nB+1): size[find(("B", k))] += int((labB == k).sum())
    main = max(size, key=size.get)
    bad = []
    for ref, pn, lays, cx, cy, w, h in gndpads:
        ok = False
        for L in lays:
            lab = labF if L == "F.Cu" else labB
            i0, j0, i1, j1 = gi(cx-w/2), gi(cy-h/2), gi(cx+w/2), gi(cy+h/2)
            ids = set(lab[j0:j1+1, i0:i1+1].ravel()) - {0}
            if any(find((L[0], k)) == main for k in ids): ok = True
        if not ok: bad.append((ref, pn, round(cx, 2), round(cy, 2)))
    print(f"GND pads on islands: {len(bad)} of {len(gndpads)}")
    for b in bad: print("  ", b)
    run.mainmask = {"F.Cu": np.isin(labF, [k for k in range(1, nF+1) if find(("F", k)) == main]),
                    "B.Cu": np.isin(labB, [k for k in range(1, nB+1) if find(("B", k)) == main])}
    return bad

if __name__ == "__main__": run()

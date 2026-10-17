"""Post-process the Freerouting result: exact DRC, rip-up + re-route violating nets, add missing links, stitch GND islands."""
import sys, math, heapq, uuid
import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion, label
sys.argv = [sys.argv[0]]
import gen_kicad2 as G, dsn

U = lambda: str(uuid.uuid4())
BW, BH = G.BW, G.BH
CLR = 0.20; DRC_CLR = 0.127; EDGE = 0.5
VIA_D = 0.5
W = {"VSYS": 0.3, "+5V": 0.3, "+3V3": 0.3, "SW5": 0.3, "SW3": 0.3, "VBAT": 0.4, "VBAT_RAW": 0.4}
LAY = ("F.Cu", "B.Cu")

# ------------------------------------------------------------------ geometry
pads = []   # dict(net, layers, shape, cx, cy, w, h, ref, num)
for cm in G.COMP:
    if not cm["pcb"]: continue
    nm = {p[0]: p[2] for p in cm["pins"]}
    for p in G.FP[cm["fp"]]["pads"]:
        if p[10] and not any(l.endswith(".Cu") for l in p[10]): continue
        cx, cy, w, h = G.pad_world(cm, p)
        pads.append(dict(net=nm.get(p[0]), layers=LAY if p[1] == "thru_hole" else (cm["pcb"][3]+".Cu",),
                         shape="circle" if p[2] == "circle" else "rect", cx=cx, cy=cy, w=w, h=h, ref=cm["ref"], num=p[0], th=p[1] == "thru_hole"))

def seg_pt_dist(a, b, p):
    ax, ay = a; bx, by = b; px, py = p; dx, dy = bx-ax, by-ay; L2 = dx*dx+dy*dy
    t = 0 if L2 == 0 else max(0, min(1, ((px-ax)*dx+(py-ay)*dy)/L2)); qx, qy = ax+t*dx, ay+t*dy
    return math.hypot(px-qx, py-qy)
def seg_seg_dist(a, b, c, d):
    def cross(o, p, q): return (p[0]-o[0])*(q[1]-o[1]) - (p[1]-o[1])*(q[0]-o[0])
    d1, d2, d3, d4 = cross(c, d, a), cross(c, d, b), cross(a, b, c), cross(a, b, d)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)) and d1 != 0 and d2 != 0 and d3 != 0 and d4 != 0: return 0.0
    return min(seg_pt_dist(a, b, c), seg_pt_dist(a, b, d), seg_pt_dist(c, d, a), seg_pt_dist(c, d, b))
def rect_pt_dist(pd, p):
    dx = max(abs(p[0]-pd["cx"]) - pd["w"]/2, 0); dy = max(abs(p[1]-pd["cy"]) - pd["h"]/2, 0); return math.hypot(dx, dy)
def pad_seg_dist(pd, a, b):
    if pd["shape"] == "circle": return max(seg_pt_dist(a, b, (pd["cx"], pd["cy"])) - pd["w"]/2, 0)
    # rect vs segment: sample + corner distances (good enough at this scale)
    n = max(2, int(math.hypot(b[0]-a[0], b[1]-a[1])/0.05)+1); best = 9
    for t in np.linspace(0, 1, n): best = min(best, rect_pt_dist(pd, (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)))
    return best
def pad_pt_dist(pd, p):
    return max(math.hypot(p[0]-pd["cx"], p[1]-pd["cy"]) - pd["w"]/2, 0) if pd["shape"] == "circle" else rect_pt_dist(pd, p)

def drc(tracks, vias, clr=DRC_CLR):
    """Return list of (kind, netA, netB, x, y)."""
    viol = []
    # spatial hash of pads by layer
    cell = 2.0
    hp = {}
    for pd in pads:
        for L in pd["layers"]:
            for i in range(int((pd["cx"]-pd["w"]/2-1)//cell), int((pd["cx"]+pd["w"]/2+1)//cell)+1):
                for j in range(int((pd["cy"]-pd["h"]/2-1)//cell), int((pd["cy"]+pd["h"]/2+1)//cell)+1): hp.setdefault((L, i, j), []).append(pd)
    def near_pads(L, x0, y0, x1, y1):
        out = set(); res = []
        for i in range(int((min(x0, x1)-1)//cell), int((max(x0, x1)+1)//cell)+1):
            for j in range(int((min(y0, y1)-1)//cell), int((max(y0, y1)+1)//cell)+1):
                for pd in hp.get((L, i, j), []):
                    if id(pd) not in out: out.add(id(pd)); res.append(pd)
        return res
    for k, (net, L, a, b, w) in enumerate(tracks):
        for pd in near_pads(L, a[0], a[1], b[0], b[1]):
            if pd["net"] == net: continue
            d = pad_seg_dist(pd, a, b) - w/2
            if d < clr - 1e-6: viol.append(("track-pad", net, f'{pd["ref"]}-{pd["num"]}({pd["net"]})', round((a[0]+b[0])/2, 2), round((a[1]+b[1])/2, 2), round(d, 3)))
        # edge
        for pt in (a, b):
            if min(pt[0], pt[1], BW-pt[0], BH-pt[1]) - w/2 < EDGE - 1e-6: viol.append(("track-edge", net, "edge", pt[0], pt[1], 0))
    for (net, x, y) in vias:
        for L in LAY:
            for pd in near_pads(L, x, y, x, y):
                if pd["net"] == net: continue
                d = pad_pt_dist(pd, (x, y)) - VIA_D/2
                if d < clr - 1e-6: viol.append(("via-pad", net, f'{pd["ref"]}-{pd["num"]}({pd["net"]})', round(x, 2), round(y, 2), round(d, 3)))
    # track-track / track-via / via-via
    ht = {}
    for k, (net, L, a, b, w) in enumerate(tracks):
        for i in range(int((min(a[0], b[0])-1)//cell), int((max(a[0], b[0])+1)//cell)+1):
            for j in range(int((min(a[1], b[1])-1)//cell), int((max(a[1], b[1])+1)//cell)+1): ht.setdefault((L, i, j), []).append(k)
    seen = set()
    for key, ks in ht.items():
        for i1 in range(len(ks)):
            for i2 in range(i1+1, len(ks)):
                k1, k2 = ks[i1], ks[i2]
                if (k1, k2) in seen: continue
                seen.add((k1, k2)); n1, L1, a1, b1, w1 = tracks[k1]; n2, L2, a2, b2, w2 = tracks[k2]
                if n1 == n2: continue
                d = seg_seg_dist(a1, b1, a2, b2) - w1/2 - w2/2
                if d < clr - 1e-6: viol.append(("track-track", n1, n2, round((a1[0]+b1[0])/2, 2), round((a1[1]+b1[1])/2, 2), round(d, 3)))
    for (net, x, y) in vias:
        for L in LAY:
            for k in set(ht.get((L, int(x//cell), int(y//cell)), []) + ht.get((L, int((x-1)//cell), int((y-1)//cell)), []) + ht.get((L, int((x+1)//cell), int((y+1)//cell)), []) + ht.get((L, int((x-1)//cell), int((y+1)//cell)), []) + ht.get((L, int((x+1)//cell), int((y-1)//cell)), [])):
                n1, L1, a1, b1, w1 = tracks[k]
                if n1 == net: continue
                d = seg_pt_dist(a1, b1, (x, y)) - w1/2 - VIA_D/2
                if d < clr - 1e-6: viol.append(("via-track", net, n1, round(x, 2), round(y, 2), round(d, 3)))
    for i in range(len(vias)):
        for j in range(i+1, len(vias)):
            n1, x1, y1 = vias[i]; n2, x2, y2 = vias[j]
            if n1 == n2: continue
            d = math.hypot(x1-x2, y1-y2) - VIA_D
            if d < clr - 1e-6: viol.append(("via-via", n1, n2, round(x1, 2), round(y1, 2), round(d, 3)))
    return viol

# ------------------------------------------------------------------ grid router (for repairs)
RES = 0.05
NX, NY = int(round(BW/RES))+1, int(round(BH/RES))+1
gi = lambda v: int(round(v/RES))
def disc(r):
    n = int(math.ceil(r/RES)); y, x = np.ogrid[-n:n+1, -n:n+1]; return (x*x+y*y) <= (r/RES)**2+1e-9
def build_occ(tracks, vias):
    occ = {L: -np.ones((NY, NX), np.int32) for L in LAY}; padm = np.zeros((NY, NX), bool)
    def stamp_disc(L, x, y, r, nid):
        d = disc(r); n = d.shape[0]//2; j, i = gi(y), gi(x)
        j0, i0, j1, i1 = max(0, j-n), max(0, i-n), min(NY, j+n+1), min(NX, i+n+1)
        sub = d[(j0-(j-n)):(n+1+(j1-1-j)), (i0-(i-n)):(n+1+(i1-1-i))]
        reg = occ[L][j0:j1, i0:i1]; reg[sub & (reg == -1)] = nid
    for pd in pads:
        nid = G.NETID.get(pd["net"], 9999)
        for L in pd["layers"]:
            if pd["shape"] == "circle": stamp_disc(L, pd["cx"], pd["cy"], pd["w"]/2, nid)
            else:
                i0, j0, i1, j1 = gi(pd["cx"]-pd["w"]/2), gi(pd["cy"]-pd["h"]/2), gi(pd["cx"]+pd["w"]/2), gi(pd["cy"]+pd["h"]/2)
                occ[L][j0:j1+1, i0:i1+1] = nid
            i0, j0, i1, j1 = gi(pd["cx"]-pd["w"]/2), gi(pd["cy"]-pd["h"]/2), gi(pd["cx"]+pd["w"]/2), gi(pd["cy"]+pd["h"]/2); padm[j0:j1+1, i0:i1+1] = True
    for (net, L, a, b, w) in tracks:
        n = max(2, int(math.hypot(b[0]-a[0], b[1]-a[1])/RES)+1)
        for t in np.linspace(0, 1, n): stamp_disc(L, a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, w/2, G.NETID[net])
    for (net, x, y) in vias:
        for L in LAY: stamp_disc(L, x, y, VIA_D/2, G.NETID[net])
    return occ, padm
edge = np.ones((NY, NX), bool); m = gi(EDGE); edge[m:NY-m, m:NX-m] = False
DIRS = [(0, 1, 1.0), (0, -1, 1.0), (1, 0, 1.0), (-1, 0, 1.0), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
def astar(sources, targets, obs, via_ok, goal):
    gx, gy = gi(goal[0]), gi(goal[1]); best = {}; heap = []; parent = {}
    for s in sources: best[s] = 0.0; heapq.heappush(heap, (math.hypot(s[2]-gx, s[1]-gy), 0.0, s, None, -1))
    while heap:
        f, g, key, par, d = heapq.heappop(heap)
        if key in parent: continue
        parent[key] = par
        if key in targets:
            path = []; k = key
            while k is not None: path.append(k); k = parent[k]
            return path[::-1]
        l, j, i = key; ob = obs[LAY[l]]
        for di, (dj, dii, cost) in enumerate(DIRS):
            nj, ni = j+dj, i+dii
            if nj < 0 or ni < 0 or nj >= NY or ni >= NX or ob[nj, ni]: continue
            ng = g + cost + (0.3 if d != -1 and d != di else 0)
            nk = (l, nj, ni)
            if ng < best.get(nk, 1e9): best[nk] = ng; heapq.heappush(heap, (ng+math.hypot(ni-gx, nj-gy)*0.99, ng, nk, key, di))
        if via_ok[j, i]:
            nk = (1-l, j, i); ng = g + 20
            if ng < best.get(nk, 1e9): best[nk] = ng; heapq.heappush(heap, (ng+math.hypot(i-gx, j-gy)*0.99, ng, nk, key, -1))
    return None
def path_to_geom(path, net, w):
    tr = []; vs = []; run = [path[0]]
    def flush(run):
        if len(run) < 2: return
        pts = [(c[2]*RES, c[1]*RES) for c in run]; simp = [pts[0]]
        for q in range(1, len(pts)-1):
            d1 = (round(pts[q][0]-pts[q-1][0], 3), round(pts[q][1]-pts[q-1][1], 3)); d2 = (round(pts[q+1][0]-pts[q][0], 3), round(pts[q+1][1]-pts[q][1], 3))
            if d1 != d2: simp.append(pts[q])
        simp.append(pts[-1])
        for a, b in zip(simp, simp[1:]): tr.append((net, LAY[run[0][0]], a, b, w))
    for a, b in zip(path, path[1:]):
        if a[0] != b[0]: flush(run); vs.append((net, b[2]*RES, b[1]*RES)); run = [b]
        else: run.append(b)
    flush(run); return tr, vs

def route_connection(tracks, vias, net, src_cells_fn, tgt_cells_fn, w, goal, clr=None):
    clr = CLR if clr is None else clr
    occ, padm = build_occ(tracks, vias); nid = G.NETID[net]
    obs = {};
    for L in LAY:
        other = (occ[L] != -1) & (occ[L] != nid); obs[L] = (binary_dilation(other, structure=disc(w/2+clr)) | edge) & ~binary_erosion(occ[L] == nid, structure=disc(w/2))
    via_ok = ~(binary_dilation((occ["F.Cu"] != -1) & (occ["F.Cu"] != nid), structure=disc(VIA_D/2+clr+0.04)) | binary_dilation((occ["B.Cu"] != -1) & (occ["B.Cu"] != nid), structure=disc(VIA_D/2+clr+0.04)) | padm | edge)
    src = src_cells_fn(occ); tgt = tgt_cells_fn(occ)
    if not src or not tgt: return None
    path = astar(src, tgt, obs, via_ok, goal)
    if path is None: return None
    return path_to_geom(path, net, w)

def net_cells(occ, nid):
    out = set()
    for l, L in enumerate(LAY):
        for j, i in zip(*np.nonzero(occ[L] == nid)): out.add((l, int(j), int(i)))
    return out
def pad_cells(pd):
    out = set()
    for L in pd["layers"]:
        l = LAY.index(L)
        for j in range(gi(pd["cy"]-pd["h"]/2), gi(pd["cy"]+pd["h"]/2)+1):
            for i in range(gi(pd["cx"]-pd["w"]/2), gi(pd["cx"]+pd["w"]/2)+1): out.add((l, j, i))
    return out

NAMES = {v: k for k, v in G.NETID.items()}
def corridor_nets(tracks, vias, pd, own):
    """Nets (other than own) whose tracks/vias occupy the escape corridors around pad pd."""
    occ, padm = build_occ(tracks, vias); found = set()
    ext = 1.2; half = max(pd["w"], pd["h"])/2 + 0.25
    boxes = [(pd["cx"]-half, pd["cy"]-pd["h"]/2-ext, pd["cx"]+half, pd["cy"]+pd["h"]/2+ext), (pd["cx"]-pd["w"]/2-ext, pd["cy"]-half, pd["cx"]+pd["w"]/2+ext, pd["cy"]+half)]
    for L in pd["layers"]:
        for (x0, y0, x1, y1) in boxes:
            sub = occ[L][gi(y0):gi(y1)+1, gi(x0):gi(x1)+1]; pm = padm[gi(y0):gi(y1)+1, gi(x0):gi(x1)+1]
            for v in set(sub[(sub != -1) & ~pm].ravel()):
                n = NAMES.get(int(v))
                if n and n != own and n != "GND": found.add(n)
    return found
def connected_cells(occ, nid, seed_pads, vias):
    """Own-net copper cells connected (through same-layer copper, own vias and TH pads) to the seed pads."""
    labs = {L: label(occ[L] == nid)[0] for L in LAY}
    comps = set()
    for pd in seed_pads:
        for L in pd["layers"]:
            k = labs[L][gi(pd["cy"]), gi(pd["cx"])]
            if k: comps.add((L, int(k)))
    for _ in range(4):   # closure across layers through own vias / TH pads
        for (n, x, y) in vias:
            if n != NAMES.get(nid): continue
            kf, kb = labs["F.Cu"][gi(y), gi(x)], labs["B.Cu"][gi(y), gi(x)]
            if kf and kb and ((("F.Cu", int(kf)) in comps) or (("B.Cu", int(kb)) in comps)): comps.add(("F.Cu", int(kf))); comps.add(("B.Cu", int(kb)))
        for pd in pads:
            if pd["net"] != NAMES.get(nid) or not pd["th"]: continue
            kf, kb = labs["F.Cu"][gi(pd["cy"]), gi(pd["cx"])], labs["B.Cu"][gi(pd["cy"]), gi(pd["cx"])]
            if kf and kb and ((("F.Cu", int(kf)) in comps) or (("B.Cu", int(kb)) in comps)): comps.add(("F.Cu", int(kf))); comps.add(("B.Cu", int(kb)))
    out = set()
    for (L, k) in comps:
        l = LAY.index(L)
        for j, i in zip(*np.nonzero(labs[L] == k)): out.add((l, int(j), int(i)))
    return out

def reroute_net(tracks, vias, net):
    w = W.get(net, 0.2); plist = [p for p in pads if p["net"] == net]; nid = G.NETID[net]
    done = [plist[0]]; rem = plist[1:]; ok = True
    while rem:
        cur = done[-1]; rem.sort(key=lambda p: (p["cx"]-cur["cx"])**2+(p["cy"]-cur["cy"])**2); tgt = rem.pop(0)
        srcf = lambda occ, d=list(done): connected_cells(occ, nid, d, vias) - pad_cells(tgt)
        res = None
        for (ww, cc) in ((w, None), (0.2, 0.13), (0.15, 0.13)):
            res = route_connection(tracks, vias, net, srcf, lambda occ: pad_cells(tgt), ww, (tgt["cx"], tgt["cy"]), clr=cc)
            if res and (res[0] or res[1]): break
            res = None
        if res is None:
            # already touching? (target pad overlapping own copper of the done group)
            occ, padm = build_occ(tracks, vias)
            if srcf(occ) & pad_cells(tgt): done.append(tgt); continue
            print(f"  !! {net}: cannot reach {tgt['ref']}-{tgt['num']} after rip"); ok = False
        else: tracks += res[0]; vias += res[1]
        done.append(tgt)
    return ok

def connect_with_rip(tracks, vias, net, srcf, pd, w, tries=2):
    """Try to connect pad pd to srcf; if impossible, rip nets in its escape corridors and retry, then re-route them."""
    for attempt in range(tries+1):
        for (ww, cc) in ((w, None), (0.2, 0.13), (0.15, 0.13)):
            res = route_connection(tracks, vias, net, srcf, lambda occ: pad_cells(pd), ww, (pd["cx"], pd["cy"]), clr=cc)
            if res: tracks += res[0]; vias += res[1]; return True, tracks, vias
        if attempt == tries: break
        rip = {n for n in corridor_nets(tracks, vias, pd, net) if len([p for p in pads if p["net"] == n]) <= 6}
        if not rip: break
        print(f"    ripping {sorted(rip)} to free {pd['ref']}-{pd['num']}")
        tracks = [t for t in tracks if t[0] not in rip]; vias = [v for v in vias if v[0] not in rip]
        res = None
        for (ww, cc) in ((w, None), (0.2, 0.13), (0.15, 0.13)):
            res = route_connection(tracks, vias, net, srcf, lambda occ: pad_cells(pd), ww, (pd["cx"], pd["cy"]), clr=cc)
            if res: break
        if res: tracks += res[0]; vias += res[1]
        for n in sorted(rip, key=lambda n: len([p for p in pads if p["net"] == n])): reroute_net(tracks, vias, n)
        if res: return True, tracks, vias
    return False, tracks, vias

# ------------------------------------------------------------------ main
def main():
    tracks, vias = dsn.parse_ses()
    tracks = [(n, L, a, b, w) for (n, L, a, b, w) in tracks if n in G.NETID]; vias = [(n, x, y) for (n, x, y) in vias if n in G.NETID]
    v = drc(tracks, vias); print(f"exact DRC on Freerouting result: {len(v)} violations")
    for x in v[:40]: print("  ", x)
    # rip up nets involved (prefer ripping the non-power net of a pair)
    rip = set()
    for kind, n1, n2, x, y, d in v:
        if kind in ("track-pad", "via-pad", "track-edge"): rip.add(n1)
        else: rip.add(n2 if n1 in W else n1)
    print("rip-up nets:", sorted(rip))
    kept_t = [t for t in tracks if t[0] not in rip]; kept_v = [vv for vv in vias if vv[0] not in rip]
    # re-route ripped nets pad by pad (nearest-neighbour chaining)
    for net in sorted(rip, key=lambda n: len([p for p in pads if p["net"] == n])):
        w = W.get(net, 0.2); plist = [p for p in pads if p["net"] == net]
        nid = G.NETID[net]; done = [plist[0]]; rem = plist[1:]
        while rem:
            cur = done[-1]; rem.sort(key=lambda p: (p["cx"]-cur["cx"])**2+(p["cy"]-cur["cy"])**2); tgt = rem.pop(0)
            res = route_connection(kept_t, kept_v, net, lambda occ: net_cells(occ, nid), lambda occ: pad_cells(tgt), w, (tgt["cx"], tgt["cy"]))
            if res is None: print(f"  !! {net}: cannot reach {tgt['ref']}-{tgt['num']}")
            else: kept_t += res[0]; kept_v += res[1]
            done.append(tgt)
    tracks, vias = kept_t, kept_v
    # missing connections reported by Freerouting: re-check every net's connectivity with the occupancy grid
    occ, padm = build_occ(tracks, vias)
    for net in G.NETS:
        if net == "GND": continue
        nid = G.NETID[net]; plist = [p for p in pads if p["net"] == net]
        if len(plist) < 2: continue
        labs = {L: label(occ[L] == nid)[0] for L in LAY}
        # union across layers through vias / TH pads
        parent = {}
        def find(a):
            while parent.get(a, a) != a: a = parent[a]
            return a
        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb: parent[ra] = rb
        for (n, x, y) in vias:
            if n == net and labs["F.Cu"][gi(y), gi(x)] and labs["B.Cu"][gi(y), gi(x)]: union(("F", labs["F.Cu"][gi(y), gi(x)]), ("B", labs["B.Cu"][gi(y), gi(x)]))
        for pd in plist:
            if pd["th"]: union(("F", labs["F.Cu"][gi(pd["cy"]), gi(pd["cx"])]), ("B", labs["B.Cu"][gi(pd["cy"]), gi(pd["cx"])]))
        comp = {}
        for pd in plist:
            L = pd["layers"][0]; comp[pd["ref"]+"-"+pd["num"]] = find((L[0], labs[L][gi(pd["cy"]), gi(pd["cx"])]))
        groups = {}
        for k, c in comp.items(): groups.setdefault(c, []).append(k)
        if len(groups) > 1:
            print(f"  {net}: {len(groups)} islands -> connecting")
            gl = sorted(groups.values(), key=len, reverse=True)
            for grp in gl[1:]:
                pd = [p for p in plist if p["ref"]+"-"+p["num"] == grp[0]][0]
                main_pads = [p for p in plist if p["ref"]+"-"+p["num"] in gl[0]]
                srcf = lambda occ: set().union(*[pad_cells(p) for p in main_pads])
                ok, tracks, vias = connect_with_rip(tracks, vias, net, srcf, pd, W.get(net, 0.2))
                if not ok: print(f"  !! {net}: still cannot connect {grp[0]}")
    # GND island stitching
    import gndcheck
    dsn_tracks_backup = dsn.parse_ses
    dsn.parse_ses = lambda: (tracks, vias)
    bad = gndcheck.run()
    gid = G.NETID["GND"]
    for (ref, pn, cx, cy) in bad:
        pd = [p for p in pads if p["ref"] == ref and p["num"] == pn][0]
        occ, padm = build_occ(tracks, vias)
        # targets: cells of the main GND pour (eroded so the track fits), within 5 mm
        mm = gndcheck.run.mainmask; tg = set()
        for l, L in enumerate(LAY):
            er = binary_erosion(mm[L], structure=disc(0.12))
            j0, j1, i0, i1 = max(0, gi(cy-5)), min(NY, gi(cy+5)), max(0, gi(cx-5)), min(NX, gi(cx+5))
            for j, i in zip(*np.nonzero(er[j0:j1, i0:i1])): tg.add((l, int(j+j0), int(i+i0)))
        res = None
        if tg:
            for (ww, cc) in ((0.2, None), (0.2, 0.13), (0.15, 0.13)):
                res = route_connection(tracks, vias, "GND", lambda occ: pad_cells(pd), lambda occ: tg, ww, (cx, cy), clr=cc)
                if res: break
        if res: tracks += res[0]; vias += res[1]
        else:
            if res is None: print(f"  !! GND stitch failed for {ref}-{pn}")
        dsn.parse_ses = lambda: (tracks, vias); gndcheck.run()
    dsn.parse_ses = lambda: (tracks, vias)
    bad2 = gndcheck.run()
    dsn.parse_ses = dsn_tracks_backup
    v2 = drc(tracks, vias); print(f"final exact DRC: {len(v2)} violations")
    for x in v2[:30]: print("  ", x)
    dsn.write(tracks, vias)
    return tracks, vias

if __name__ == "__main__": main()

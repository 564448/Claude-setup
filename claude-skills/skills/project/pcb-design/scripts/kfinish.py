"""Finish a KiCad board on exact geometry (from kdump.json): route missing links, stitch GND islands. Writes kfinish.json."""
import json, math, sys, heapq
sys.argv = ['x']
import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion, label
from matplotlib.path import Path
d = json.load(open("kdump.json")); isl = [x for x in d["islands"] if x["layer"] in ("F.Cu", "B.Cu")]; TR = [t for t in d["tracks"] if t[1] in ("F.Cu", "B.Cu")]; VI = d["vias"]; PD = d["pads"]
import os as _os
SKIPSTITCH = _os.environ.get("SKIPSTITCH") == "1"
BW, BH = 40.0, 45.0; RES = 0.05; NX, NY = int(BW/RES)+1, int(BH/RES)+1; gi = lambda v: int(round(v/RES)); LAY = ("F.Cu", "B.Cu")
def disc(r):
    n = int(math.ceil(r/RES)); y, x = np.ogrid[-n:n+1, -n:n+1]; return (x*x+y*y) <= (r/RES)**2+1e-9
def seg_pt(a, b, p):
    ax, ay = a; bx, by = b; px, py = p; dx, dy = bx-ax, by-ay; L2 = dx*dx+dy*dy; t = 0 if L2 == 0 else max(0, min(1, ((px-ax)*dx+(py-ay)*dy)/L2)); return math.hypot(px-ax-t*dx, py-ay-t*dy)
NID = {n: i+1 for i, n in enumerate(sorted({t[0] for t in TR} | {v[0] for v in VI} | {p[0] for p in PD if p[0]} | {"GND"}))}
def layers_of(p): return LAY if p[7] else tuple(l for l in p[8] if l in LAY)
def build():
    occ = {L: -np.ones((NY, NX), np.int32) for L in LAY}; padm = np.zeros((NY, NX), bool)
    def stamp(L, x, y, r, nid):
        dd = disc(r); n = dd.shape[0]//2; j, i = gi(y), gi(x); j0, i0, j1, i1 = max(0, j-n), max(0, i-n), min(NY, j+n+1), min(NX, i+n+1)
        sub = dd[(j0-(j-n)):(n+1+(j1-1-j)), (i0-(i-n)):(n+1+(i1-1-i))]; reg = occ[L][j0:j1, i0:i1]; reg[sub & (reg == -1)] = nid
    for p in PD:
        nid = NID.get(p[0], 9999) if p[0] else 9999
        for L in layers_of(p):
            i0, j0, i1, j1 = gi(p[3]-p[5]/2), gi(p[4]-p[6]/2), gi(p[3]+p[5]/2), gi(p[4]+p[6]/2); occ[L][j0:j1+1, i0:i1+1] = nid; padm[j0:j1+1, i0:i1+1] = True
    for t in TR:
        n = max(2, int(math.hypot(t[4]-t[2], t[5]-t[3])/RES)+1)
        for s in np.linspace(0, 1, n): stamp(t[1], t[2]+(t[4]-t[2])*s, t[3]+(t[5]-t[3])*s, t[6]/2, NID[t[0]])
    for v in VI:
        for L in LAY: stamp(L, v[1], v[2], v[3]/2, NID[v[0]])
    return occ, padm
edge = np.ones((NY, NX), bool); m = gi(0.6); edge[m:NY-m, m:NX-m] = False
DIRS = [(0, 1, 1.0), (0, -1, 1.0), (1, 0, 1.0), (-1, 0, 1.0), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
def astar(src, tgt, obs, via_ok, goal):
    gx, gy = gi(goal[0]), gi(goal[1]); best = {}; heap = []; parent = {}
    for s in src: best[s] = 0.0; heapq.heappush(heap, (math.hypot(s[2]-gx, s[1]-gy), 0.0, s, None, -1))
    while heap:
        f, g, key, par, dd = heapq.heappop(heap)
        if key in parent: continue
        parent[key] = par
        if key in tgt:
            path = []; k = key
            while k is not None: path.append(k); k = parent[k]
            return path[::-1]
        l, j, i = key; ob = obs[LAY[l]]
        for di, (dj, dii, c) in enumerate(DIRS):
            nj, ni = j+dj, i+dii
            if nj < 0 or ni < 0 or nj >= NY or ni >= NX or ob[nj, ni]: continue
            ng = g+c+(0.3 if dd != -1 and dd != di else 0); nk = (l, nj, ni)
            if ng < best.get(nk, 1e9): best[nk] = ng; heapq.heappush(heap, (ng+math.hypot(ni-gx, nj-gy)*0.99, ng, nk, key, di))
        if via_ok[j, i]:
            nk = (1-l, j, i); ng = g+20
            if ng < best.get(nk, 1e9): best[nk] = ng; heapq.heappush(heap, (ng+math.hypot(i-gx, j-gy)*0.99, ng, nk, key, -1))
    return None
def route(net, src_cells, tgt_cells, w, goal, clr=0.16):
    occ, padm = build(); nid = NID[net]; obs = {}
    for L in LAY:
        other = (occ[L] != -1) & (occ[L] != nid); obs[L] = (binary_dilation(other, structure=disc(w/2+clr)) | edge) & ~binary_erosion(occ[L] == nid, structure=disc(w/2))
    holes = np.zeros((NY, NX), bool)
    for v in VI: holes[gi(v[2]), gi(v[1])] = True
    for p in PD:
        if p[7]: holes[gi(p[4]), gi(p[3])] = True
    via_ok = ~(binary_dilation((occ["F.Cu"] != -1) & (occ["F.Cu"] != nid), structure=disc(0.2+clr+0.05)) | binary_dilation((occ["B.Cu"] != -1) & (occ["B.Cu"] != nid), structure=disc(0.2+clr+0.05)) | binary_dilation(holes, structure=disc(0.2+0.3+0.25)) | padm | edge)
    src = src_cells(occ); tgt = tgt_cells(occ)
    if not src or not tgt: return None
    path = astar(src, tgt, obs, via_ok, goal)
    if not path: return None
    tr = []; vs = []; run = [path[0]]
    def flush(run):
        if len(run) < 2: return
        pts = [(c[2]*RES, c[1]*RES) for c in run]; simp = [pts[0]]
        for q in range(1, len(pts)-1):
            d1 = (round(pts[q][0]-pts[q-1][0], 3), round(pts[q][1]-pts[q-1][1], 3)); d2 = (round(pts[q+1][0]-pts[q][0], 3), round(pts[q+1][1]-pts[q][1], 3))
            if d1 != d2: simp.append(pts[q])
        simp.append(pts[-1])
        for a, b in zip(simp, simp[1:]): tr.append([net, LAY[run[0][0]], a[0], a[1], b[0], b[1], w])
    for a, b in zip(path, path[1:]):
        if a[0] != b[0]: flush(run); vs.append([net, b[2]*RES, b[1]*RES, 0.4]); run = [b]
        else: run.append(b)
    flush(run); return tr, vs
def pad_cells(p):
    out = set()
    for L in layers_of(p):
        l = LAY.index(L)
        for j in range(gi(p[4]-p[6]/2), gi(p[4]+p[6]/2)+1):
            for i in range(gi(p[3]-p[5]/2), gi(p[3]+p[5]/2)+1): out.add((l, j, i))
    return out
def groups(net):
    occ, padm = build(); nid = NID[net]; plist = [p for p in PD if p[0] == net]
    labs = {L: label(occ[L] == nid)[0] for L in LAY}; parent = {}
    def find(a):
        while parent.get(a, a) != a: a = parent[a]
        return a
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    for v in VI:
        if v[0] == net and labs["F.Cu"][gi(v[2]), gi(v[1])] and labs["B.Cu"][gi(v[2]), gi(v[1])]: union(("F", labs["F.Cu"][gi(v[2]), gi(v[1])]), ("B", labs["B.Cu"][gi(v[2]), gi(v[1])]))
    for p in plist:
        if p[7]: union(("F", labs["F.Cu"][gi(p[4]), gi(p[3])]), ("B", labs["B.Cu"][gi(p[4]), gi(p[3])]))
    grp = {}
    for p in plist:
        L = layers_of(p)[0]; grp.setdefault(find((L[0], labs[L][gi(p[4]), gi(p[3])])), []).append(p)
    return sorted(grp.values(), key=len, reverse=True), labs
new_tr = []; new_vi = []
import os
NETS_ONLY = [n for n in os.environ.get("NETS","").split(",") if n]
RCLR = float(os.environ.get("CLR","0.2"))
for net in [n for n in NID if n != "GND" and n and (not NETS_ONLY or n in NETS_ONLY)]:
    for _ in range(4):
        gl, labs = groups(net)
        if len(gl) <= 1: break
        main, other = gl[0], gl[1]; nid = NID[net]
        def srcf(occ, main=main, nid=nid, net=net):
            out = set(); ls = {L: label(occ[L] == nid)[0] for L in LAY}; comps = set()
            for p in main:
                for L in layers_of(p):
                    k = ls[L][gi(p[4]), gi(p[3])]
                    if k: comps.add((L, int(k)))
            for v in VI:
                if v[0] != net: continue
                kf, kb = ls["F.Cu"][gi(v[2]), gi(v[1])], ls["B.Cu"][gi(v[2]), gi(v[1])]
                if kf and kb and (("F.Cu", int(kf)) in comps or ("B.Cu", int(kb)) in comps): comps.add(("F.Cu", int(kf))); comps.add(("B.Cu", int(kb)))
            for (L, k) in comps:
                for j, i in zip(*np.nonzero(ls[L] == k)): out.add((LAY.index(L), int(j), int(i)))
            return out
        res = None
        for (w, c) in ((0.2, RCLR), (0.2, 0.16), (0.15, 0.14), (0.15, 0.13)):
            for p in other:
                res = route(net, srcf, lambda occ, p=p: pad_cells(p), w, (p[3], p[4]), c)
                if res: break
            if res: break
        if res: TR.extend(res[0]); VI.extend(res[1]); new_tr += res[0]; new_vi += res[1]; print(f"linked {net}: +{len(res[0])} segs, +{len(res[1])} vias")
        else: print(f"!! {net}: cannot link {[p[1]+'-'+p[2] for p in other]}"); break
mainB = max((x for x in isl if x["layer"] == "B.Cu"), key=lambda x: x["area"]); mainF = max((x for x in isl if x["layer"] == "F.Cu"), key=lambda x: x["area"]); mBp = Path(mainB["pts"]); mFp = Path(mainF["pts"])
def clear(x, y, r, c=0.15):
    for p in PD:
        if p[0] == "GND": continue
        if math.hypot(max(abs(x-p[3])-p[5]/2, 0), max(abs(y-p[4])-p[6]/2, 0)) < r+c: return False
        if p[7] and math.hypot(x-p[3], y-p[4]) < r+p[5]/2+0.26: return False
    for t in TR:
        if t[0] != "GND" and seg_pt((t[2], t[3]), (t[4], t[5]), (x, y))-t[6]/2 < r+c: return False
    for v in VI:
        if math.hypot(x-v[1], y-v[2]) < r+v[3]/2+0.26: return False
    return 0.75 <= x <= BW-0.75 and 0.75 <= y <= BH-0.75
polys = [(x["layer"], Path(x["pts"]), x) for x in isl]
def accepted(layer):
    """polygons on `layer` that are connected to main GND: main itself, or containing a TH GND pad"""
    out = [p for (L, p, x) in polys if L == layer and (x is mainB or x is mainF)]
    for (L, p, x) in polys:
        if L == layer and any(q[0] == "GND" and q[7] and p.contains_point((q[3], q[4])) for q in PD): out.append(p)
    return out
ACC = {"F.Cu": accepted("F.Cu"), "B.Cu": accepted("B.Cu")}
def in_acc(layer, pt): return any(p.contains_point(pt) for p in ACC[layer])
def connected(path, layer):
    other = "B.Cu" if layer == "F.Cu" else "F.Cu"
    for v in VI:
        if v[0] == "GND" and path.contains_point((v[1], v[2])) and in_acc(other, (v[1], v[2])): return True
    for p in PD:
        if p[0] == "GND" and p[7] and path.contains_point((p[3], p[4])): return True
    for t in TR:   # a GND track leaving the island to accepted copper on the same layer or ending on a via/TH pad
        if t[0] != "GND" or t[1] != layer: continue
        a, bq = (t[2], t[3]), (t[4], t[5])
        for inside, outside in ((a, bq), (bq, a)):
            if path.contains_point(inside) and not path.contains_point(outside):
                if in_acc(layer, outside): return True
                if any(v[0] == "GND" and abs(v[1]-outside[0]) < 0.05 and abs(v[2]-outside[1]) < 0.05 and in_acc(other, outside) for v in VI): return True
    return False
nst = 0; miss = []
for x in ([] if SKIPSTITCH else isl):
    if x is mainB or x is mainF: continue
    path = Path(x["pts"])
    if connected(path, x["layer"]): continue
    xs = [p[0] for p in x["pts"]]; ys = [p[1] for p in x["pts"]]; best = None; bs = -1
    other = mBp if x["layer"] == "F.Cu" else mFp
    for gx in np.arange(min(xs), max(xs)+0.01, 0.02):
        for gy in np.arange(min(ys), max(ys)+0.01, 0.02):
            if path.contains_point((gx, gy)) and in_acc("B.Cu" if x["layer"] == "F.Cu" else "F.Cu", (gx, gy)) and clear(gx, gy, 0.2, 0.13):
                sc = min(seg_pt(x["pts"][k], x["pts"][(k+1) % len(x["pts"])], (gx, gy)) for k in range(len(x["pts"])))
                if sc > bs: bs = sc; best = (gx, gy)
    if best: VI.append(["GND", best[0], best[1], 0.4]); new_vi.append(["GND", best[0], best[1], 0.4]); nst += 1
    else:
        # no via fits: route a GND track from the island to the main pour (either layer, vias allowed)
        l_isl = LAY.index(x["layer"])
        def tgtf(occ, path=path, l=l_isl, xs=xs, ys=ys):
            out = set()
            for gx in np.arange(min(xs), max(xs)+0.01, RES):
                for gy in np.arange(min(ys), max(ys)+0.01, RES):
                    if path.contains_point((gx, gy)): out.add((l, gi(gy), gi(gx)))
            return out
        def srcf(occ):
            out = set()
            for (poly, l) in ((mFp, 0), (mBp, 1)):
                bb = poly.get_extents()
                for gx in np.arange(max(0.6, bb.x0), min(BW-0.6, bb.x1), 0.15):
                    for gy in np.arange(max(0.6, bb.y0), min(BH-0.6, bb.y1), 0.15):
                        if poly.contains_point((gx, gy)) and all(poly.contains_point((gx+dx, gy+dy)) for dx, dy in ((0.25, 0), (-0.25, 0), (0, 0.25), (0, -0.25))): out.add((l, gi(gy), gi(gx)))
            return out
        cx, cy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
        res = route("GND", srcf, tgtf, 0.2, (cx, cy), 0.2) or route("GND", srcf, tgtf, 0.15, (cx, cy), 0.16)
        if res: TR.extend(res[0]); VI.extend(res[1]); new_tr += res[0]; new_vi += res[1]; nst += 1; print(f"   island at ({min(xs):.1f},{min(ys):.1f}) linked by track: +{len(res[0])} segs +{len(res[1])} vias")
        else: miss.append((x["layer"], round(x["area"], 1), round(min(xs), 1), round(min(ys), 1)))
print(f"stitching vias: {nst}; islands without a spot: {miss}")
json.dump({"tracks": new_tr, "vias": new_vi}, open("kfinish.json", "w")); print("kfinish.json written")

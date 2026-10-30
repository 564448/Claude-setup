"""Export the CanSat board to Specctra DSN, run Freerouting, import the .ses back into the KiCad PCB."""
import sys, os, re, math, subprocess, uuid, time
sys.argv = [sys.argv[0]]
import gen_kicad2 as G
U = lambda: str(uuid.uuid4())
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(os.path.dirname(HERE), "tools")
JAR = os.path.join(TOOLS, "freerouting.jar")
def _find_java():
    import glob
    c = glob.glob(os.path.join(TOOLS, "jdk-*", "bin", "java.exe")) + glob.glob(os.path.join(HERE, "jre", "jdk-25*", "bin", "java.exe"))
    if not c: raise SystemExit("Java 25 not found: unzip tools/jre-25-windows-x64.zip into tools/")
    return c[0]
JAVA = _find_java()
os.makedirs(os.path.join(HERE, "fr"), exist_ok=True)
TAG = os.environ.get("CANSAT_TAG", "cansat")
DSN = os.path.join(HERE, "fr", TAG + ".dsn"); SES = os.path.join(HERE, "fr", TAG + ".ses")
BW, BH = G.BW, G.BH
CLR = 140            # um
EDGE_INSET = 0.45    # mm
VIA = "Via[0-3]_500:250_um"
W_SIG, W_MID, W_HI = 200, 300, 400
NET_W = {"VSYS": W_MID, "+5V": W_MID, "+3V3": W_MID, "SW5": W_MID, "SW3": W_MID, "VBAT": W_HI, "VBAT_RAW": W_HI, "SOL": W_SIG, "SOL_RAW": W_SIG}
um = lambda v: f"{v*1000:.1f}"

GND_EXPLICIT = {("U5","6"),("U6","1"),("U9","7"),("C19","2"),("U1","1"),("U1","16"),("U1","31"),("U2","10"),("U2","14"),("U3","39"),("U3","1"),("U3","15"),("U3","38")}

FANOUT = []   # (layer, (x0,y0), (x1,y1), width, viax, viay, net)
FANOUT_FAIL = set()
def gnd_fanout():
    import math
    allpads = []
    for cm in G.COMP:
        if not cm["pcb"]: continue
        nm = {p[0]: p[2] for p in cm["pins"]}
        for p in G.FP[cm["fp"]]["pads"]:
            if p[10] and not any(l.endswith(".Cu") for l in p[10]): continue
            cx, cy, w, h = G.pad_world(cm, p)
            allpads.append(dict(net=nm.get(p[0]), cx=cx, cy=cy, w=w, h=h, th=p[1] == "thru_hole", side=cm["pcb"][3], ref=cm["ref"], num=p[0], ox=cm["pcb"][0], oy=cm["pcb"][1], circle=p[2] == "circle"))
    def clear(x, y, r, net, side, both=False):
        for q in allpads:
            if q["net"] == net and not q["th"]: continue
            if q["net"] == net and q["th"] and math.hypot(x-q["cx"], y-q["cy"]) < r + q["w"]/2 + 0.25: return False
            if not both and not q["th"] and q["side"] != side: continue
            dx = max(abs(x-q["cx"])-q["w"]/2, 0); dy = max(abs(y-q["cy"])-q["h"]/2, 0)
            if math.hypot(dx, dy) < r + 0.14: return False
        for (L, a, b, w, vx, vy, nn) in FANOUT:
            if math.hypot(x-vx, y-vy) < 0.5 + 0.14: return False
        return 0.5+r <= x <= BW-0.5-r and 0.5+r <= y <= BH-0.5-r
    done = 0; fail = []
    for q in allpads:
        if q["net"] not in ("GND", "+3V3") or q["th"]: continue
        if q["ref"] in ("U10", "U11") and q["num"] != "17": continue      # QFN side pins: served by the EP via
        if q["ref"] in ("U10", "U11") and q["num"] == "17":
            if clear(q["cx"], q["cy"], 0.25, "GND", q["side"], both=True): FANOUT.append((q["side"]+".Cu", (q["cx"], q["cy"]), (q["cx"], q["cy"]), 0.2, q["cx"], q["cy"], q["net"])); done += 1
            else: fail.append(q["ref"]+"-EP")
            continue
        dirs = [(q["cx"]-q["ox"], q["cy"]-q["oy"])]
        dirs = [(dx/ (math.hypot(dx, dy) or 1), dy/(math.hypot(dx, dy) or 1)) for dx, dy in dirs] + [(1,0),(-1,0),(0,1),(0,-1),(0.7,0.7),(-0.7,0.7),(0.7,-0.7),(-0.7,-0.7)]
        ok = False
        for (ux, uy) in dirs:
            for d in (0.55, 0.7, 0.85, 1.0, 1.2, 1.4):
                ext = (abs(ux)*q["w"] + abs(uy)*q["h"])/2
                vx, vy = q["cx"] + ux*(ext+d), q["cy"] + uy*(ext+d)
                if clear(vx, vy, 0.25, q["net"], q["side"], both=True):
                    # stub must also be clear: sample along it
                    if all(clear(q["cx"]+ux*(ext+t*(d)), q["cy"]+uy*(ext+t*d), 0.1, q["net"], q["side"]) for t in (0.3, 0.6, 0.9)):
                        FANOUT.append((q["side"]+".Cu", (q["cx"], q["cy"]), (vx, vy), 0.2, vx, vy, q["net"])); ok = True; break
            if ok: break
        if ok: done += 1
        else: fail.append(q["ref"]+"-"+q["num"])
    print(f"GND fanout: {done} vias placed, failed for {fail}")
    global FANOUT_FAIL; FANOUT_FAIL = set(fail)
    import json; json.dump(FANOUT, open(os.path.join(HERE, "fr", TAG + "_fanout.json"), "w"))

def export():
    FANOUT.clear(); gnd_fanout()
    padstacks = {}; images = []; placements = []; netpins = {n: [] for n in G.NETS}
    for cm in G.COMP:
        if not cm["pcb"]: continue
        x, y, rot, side = cm["pcb"]; fpd = G.FP[cm["fp"]]; nm = {p[0]: p[2] for p in cm["pins"]}
        img = cm["ref"] + "_" + fpd["name"]          # one image per component (rotation/pad numbering independent)
        pins = []; seen = {}
        for p in fpd["pads"]:
            if p[10] and not any(l.endswith(".Cu") for l in p[10]): continue
            pnum, kind, shape, px, py, w, h, drill, prot, rr, layers = p
            if prot % 180 == 90: w, h = h, w
            if kind == "thru_hole":
                psn = f"Round[A]Pad_{int(w*1000)}_um" if shape == "circle" else f"Rect[A]Pad_{int(w*1000)}x{int(h*1000)}_um"
                shp = [f"(shape (circle {L} {int(w*1000)}))" if shape == "circle" else f"(shape (rect {L} {-w*500:.0f} {-h*500:.0f} {w*500:.0f} {h*500:.0f}))" for L in ("F.Cu", "In1.Cu", "In2.Cu", "B.Cu")]
            else:
                psn = f"Rect[T]Pad_{int(w*1000)}x{int(h*1000)}_um"
                shp = [f"(shape (rect F.Cu {-w*500:.0f} {-h*500:.0f} {w*500:.0f} {h*500:.0f}))"]
            padstacks[psn] = f'    (padstack "{psn}"\n      ' + "\n      ".join(shp) + "\n      (attach off)\n    )"
            pid = pnum if pnum else "NC"
            if pid in seen: seen[pid] += 1; pid = f"{pid}@{seen[pid]}"
            else: seen[pid] = 0
            pins.append(f'      (pin "{psn}" "{pid}" {um(px)} {um(-py)})')
            net = nm.get(pnum)
            if net in ("GND", "+3V3") and kind != "thru_hole" and (cm["ref"]+"-"+pnum) not in FANOUT_FAIL: net = None   # served by planes + fanout vias
            if net: netpins[net].append(f'{cm["ref"]}-{pid}')
        fx0, fy0, fx1, fy1 = fpd["fab"]
        outline = f'      (outline (path signal 0 {um(fx0)} {um(-fy0)} {um(fx1)} {um(-fy0)} {um(fx1)} {um(-fy1)} {um(fx0)} {um(-fy1)} {um(fx0)} {um(-fy0)}))'
        images.append(f'    (image "{img}"\n{outline}\n' + "\n".join(pins) + "\n    )")
        # DSN rotation is CCW with y up; KiCad's rotation is CCW on screen (y down) -> same numeric value for front,
        # for back KiCad stores mirrored coords; our generator negates y for back, which is what DSN "back" expects.
        theta = rot if side == "F" else (rot + 180) % 360   # Freerouting mirrors back images about the Y axis (verified)
        placements.append(f'    (component "{img}" (place {cm["ref"]} {um(x)} {um(-y)} {"front" if side == "F" else "back"} {theta}))')
    e = EDGE_INSET
    boundary = f"(boundary (path pcb 0 {um(e)} {um(-e)} {um(BW-e)} {um(-e)} {um(BW-e)} {um(-(BH-e))} {um(e)} {um(-(BH-e))} {um(e)} {um(-e)}))"
    planes = "\n".join(f'    (plane {n} (polygon {L} 0 {um(e)} {um(-e)} {um(BW-e)} {um(-e)} {um(BW-e)} {um(-(BH-e))} {um(e)} {um(-(BH-e))}))' for L, n in (("F.Cu", "GND"), ("B.Cu", "GND"), ("In1.Cu", "GND"), ("In2.Cu", "+3V3")))
    nets_txt = "\n".join(f'    (net "{n}" (pins {" ".join(pl)}))' for n, pl in netpins.items() if pl)
    classes = {}
    for n in G.NETS: classes.setdefault(NET_W.get(n, W_SIG), []).append(n)
    class_txt = "\n".join(f'    (class w{w} {" ".join(chr(34)+n+chr(34) for n in ns)}\n      (circuit (use_via {VIA}))\n      (rule (width {w}) (clearance {CLR})))' for w, ns in classes.items())
    dsn = f'''(pcb "cansat.dsn"
  (parser (string_quote ") (space_in_quoted_tokens on) (host_cad "gen_kicad2") (host_version "1"))
  (resolution um 10)
  (unit um)
  (structure
    (layer F.Cu (type signal) (property (index 0)))
    (layer In1.Cu (type power) (property (index 1)))
    (layer In2.Cu (type power) (property (index 2)))
    (layer B.Cu (type signal) (property (index 3)))
    {boundary}
{planes}
    (via "{VIA}")
    (rule (width {W_SIG}) (clearance {CLR}) (clearance {CLR} (type default_smd)) (clearance 100 (type smd_smd)))
  )
  (placement
{chr(10).join(placements)}
  )
  (library
{chr(10).join(images)}
{chr(10).join(padstacks.values())}
    (padstack "{VIA}"
      (shape (circle F.Cu 500))
      (shape (circle In1.Cu 500))
      (shape (circle In2.Cu 500))
      (shape (circle B.Cu 500))
      (attach off)
    )
  )
  (network
{nets_txt}
{class_txt}
  )
  (wiring
{chr(10).join(f'    (wire (path {L} 200 {um(a[0])} {um(-a[1])} {um(b[0])} {um(-b[1])}) (net {nn}) (type protect))' for (L,a,b,w,vx,vy,nn) in FANOUT)}
{chr(10).join(f'    (via "{VIA}" {um(vx)} {um(-vy)} (net {nn}) (type protect))' for (L,a,b,w,vx,vy,nn) in FANOUT)}
  )
)
'''
    open(DSN, "w", encoding="utf-8").write(dsn); print("DSN written:", DSN)

def run(passes=60, threads=None, timeout=None, heap=None):
    """Governed Freerouting run: low priority, thread + heap cap, wall-clock budget (see references/routing.md).
    Overrides: FR_THREADS, FR_TIMEOUT (seconds), FR_HEAP (e.g. 4g). Never raise these to 'remove' the limits unless asked."""
    threads = int(threads or os.environ.get("FR_THREADS", 1))
    timeout = int(timeout or os.environ.get("FR_TIMEOUT", 600))
    heap = heap or os.environ.get("FR_HEAP", "4g")
    if os.path.exists(SES): os.remove(SES)
    cmd = [JAVA, f"-Xmx{heap}", "-Djava.awt.headless=true", "-jar", JAR, "-de", DSN, "-do", SES, "-mp", str(passes), "-mt", str(threads), "-l", "en"]
    flags = subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name == "nt" else 0
    pre = (lambda: os.nice(15)) if os.name != "nt" else None
    print(f"freerouting: passes={passes} threads={threads} heap={heap} timeout={timeout}s priority=below-normal")
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(JAR), timeout=timeout, creationflags=flags, preexec_fn=pre)
    except subprocess.TimeoutExpired:
        print(f"freerouting HIT THE {timeout}s BUDGET and was killed; no .ses written. Fix placement/rules/layer count before raising the limit.")
        return False
    print(f"freerouting exit {r.returncode} in {time.time()-t0:.0f}s"); print("\n".join((r.stdout + r.stderr).splitlines()[-25:]))
    return r.returncode == 0 and os.path.exists(SES)

def parse_ses():
    import json
    fan = [tuple(x) for x in json.load(open(os.path.join(HERE, "fr", TAG + "_fanout.json")))] if os.path.exists(os.path.join(HERE, "fr", TAG + "_fanout.json")) else []
    s = open(SES, encoding="utf-8").read()
    tracks = [(f[6] if len(f) > 6 else "GND", f[0], tuple(f[1]), tuple(f[2]), f[3]) for f in fan]; vias = [(f[6] if len(f) > 6 else "GND", f[4], f[5]) for f in fan]
    for nm in re.finditer(r'\(net "?([^"\s()]+)"?\s*(.*?)\n\s*\)\n(?=\s*\((?:net|class)|\s*\)\s*\)\s*\)\s*$)', s, re.S):
        pass
    # simpler: tokenise net_out blocks
    body = s[s.index("(network_out"):]
    for nm in re.finditer(r'\(net "?([^"\s()]+)"?', body):
        net = nm.group(1); start = nm.end()
        # find matching paren
        depth = 1; i = start
        while depth:
            c = body[i]; depth += (c == "(") - (c == ")"); i += 1
        blk = body[start:i]
        for wm in re.finditer(r'\(wire\s*\(path\s+(\S+)\s+([-\d.]+)((?:\s+[-\d.]+)+)\s*\)', blk):
            layer, width, coords = wm.group(1), float(wm.group(2)), [float(v) for v in wm.group(3).split()]
            pts = [(coords[k]/10000.0, -coords[k+1]/10000.0) for k in range(0, len(coords), 2)]
            for a, b in zip(pts, pts[1:]): tracks.append((net, layer, a, b, width/10000.0))
        for vm in re.finditer(r'\(via\s+"?[^"\s()]+"?\s+([-\d.]+)\s+([-\d.]+)', blk):
            vias.append((net, float(vm.group(1))/10000.0, -float(vm.group(2))/10000.0))
    return tracks, vias

def verify(tracks, vias):
    """Every track end must touch own-net copper (pad/track/via); no track may pass near other-net pads."""
    pads = []
    for cm in G.COMP:
        if not cm["pcb"]: continue
        x, y, rot, side = cm["pcb"]; fpd = G.FP[cm["fp"]]; nm = {p[0]: p[2] for p in cm["pins"]}
        for p in fpd["pads"]:
            if p[10] and not any(l.endswith(".Cu") for l in p[10]): continue
            cx, cy, w, h = G.pad_world(cm, p)
            lay = ("F.Cu", "B.Cu") if p[1] == "thru_hole" else (side + ".Cu",)
            pads.append((nm.get(p[0]), lay, cx-w/2, cy-h/2, cx+w/2, cy+h/2, cm["ref"]))
    def in_pad(pt, L, net, tol=0.05):
        for n, lay, x0, y0, x1, y1, ref in pads:
            if n == net and L in lay and x0-tol <= pt[0] <= x1+tol and y0-tol <= pt[1] <= y1+tol: return True
        return False
    ends = {}
    for (net, L, a, b, w) in tracks:
        for pt in (a, b): ends.setdefault((net, L, round(pt[0], 3), round(pt[1], 3)), 0); ends[(net, L, round(pt[0], 3), round(pt[1], 3))] += 1
    viaset = {(net, round(x, 3), round(y, 3)) for net, x, y in vias}
    dangling = 0; wrong = 0
    for (net, L, x, y), cnt in ends.items():
        if cnt >= 2 or (net, x, y) in viaset or in_pad((x, y), L, net): continue
        dangling += 1
    for (net, L, a, b, w) in tracks:
        for t in (0.0, 0.25, 0.5, 0.75, 1.0):
            pt = (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)
            for n, lay, x0, y0, x1, y1, ref in pads:
                if n == net or L not in lay: continue
                if x0-w/2-0.1 < pt[0] < x1+w/2+0.1 and y0-w/2-0.1 < pt[1] < y1+w/2+0.1: wrong += 1; break
    print(f"verify: {dangling} dangling track ends, {wrong} track samples over other-net pads")
    return dangling, wrong

def write(tracks, vias):
    extra = []
    for (net, L, a, b, w) in tracks:
        if net not in G.NETID: continue
        extra.append(f'  (segment (start {a[0]:.4f} {a[1]:.4f}) (end {b[0]:.4f} {b[1]:.4f}) (width {w:.3f}) (layer "{L}") (net {G.NETID[net]}) (uuid "{U()}"))')
    for (net, x, y) in vias:
        if net not in G.NETID: continue
        extra.append(f'  (via (at {x:.4f} {y:.4f}) (size 0.5) (drill 0.25) (layers "F.Cu" "B.Cu") (net {G.NETID[net]}) (uuid "{U()}"))')
    gnd = G.NETID["GND"]; v33 = G.NETID["+3V3"]
    extra.append(f'  (zone (net {v33}) (net_name "+3V3") (layer "In2.Cu") (uuid "{U()}") (hatch edge 0.5) (connect_pads yes (clearance 0.2)) (min_thickness 0.2) (filled_areas_thickness no) (fill yes (thermal_gap 0.25) (thermal_bridge_width 0.3)) (polygon (pts (xy 0.3 0.3) (xy {BW-0.3} 0.3) (xy {BW-0.3} {BH-0.3}) (xy 0.3 {BH-0.3}))))')
    for L in ("F.Cu", "In1.Cu", "B.Cu"):
        extra.append(f'  (zone (net {gnd}) (net_name "GND") (layer "{L}") (uuid "{U()}") (hatch edge 0.5) (connect_pads (clearance 0.14)) (min_thickness 0.15) (filled_areas_thickness no) (fill yes (thermal_gap 0.2) (thermal_bridge_width 0.3)) (polygon (pts (xy 0.3 0.3) (xy {BW-0.3} 0.3) (xy {BW-0.3} {BH-0.3}) (xy 0.3 {BH-0.3}))))')
    G.write_schematic(); G.write_pcb_and_lib(extra)
    print(f"PCB written with {len(tracks)} segments, {len(vias)} vias")

if __name__ == "__main__":
    import sys as _s
    a = _s.argv[1:] if len(_s.argv) > 1 else []
    export()
    if not run(60): raise SystemExit("Freerouting did not produce a .ses (budget hit or error); board not modified")
    t, v = parse_ses(); verify(t, v); write(t, v)

import re, sys, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
sys.argv=['x']
import fixup as F
s=open(__import__("os").path.join(__import__("os").environ.get("CANSAT_OUT",r"C:\Knight\Project\SPACE\Cansat\hardware"),"cansat.kicad_pcb"),encoding="utf-8").read()
fig,axes=plt.subplots(1,2,figsize=(22,12))
for ax,layer,col in [(axes[0],"F.Cu","#c0392b"),(axes[1],"B.Cu","#2471a3")]:
    ax.set_xlim(-1,41); ax.set_ylim(46,-1); ax.set_aspect("equal"); ax.set_title(layer); ax.add_patch(Rectangle((0,0),40,45,fill=False,lw=2))
    for pd in F.pads:
        if layer not in pd["layers"]: continue
        if pd["shape"]=="circle": ax.add_patch(Circle((pd["cx"],pd["cy"]),pd["w"]/2,color="black",alpha=0.5))
        else: ax.add_patch(Rectangle((pd["cx"]-pd["w"]/2,pd["cy"]-pd["h"]/2),pd["w"],pd["h"],color="gray",alpha=0.7))
    seen=set()
    for pd in F.pads:
        if pd["ref"] in seen or layer not in pd["layers"]: continue
        seen.add(pd["ref"]); ax.text(pd["cx"],pd["cy"]-0.8,pd["ref"],fontsize=5,ha="center",color="green")
    for m in re.finditer(r'\(segment \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\) \(width ([-\d.]+)\) \(layer "([^"]+)"\)',s):
        if m.group(6)==layer: ax.plot([float(m.group(1)),float(m.group(3))],[float(m.group(2)),float(m.group(4))],color=col,lw=float(m.group(5))*7,solid_capstyle="round",alpha=0.9)
    for m in re.finditer(r'\(via \(at ([-\d.]+) ([-\d.]+)\)',s): ax.add_patch(Circle((float(m.group(1)),float(m.group(2))),0.25,color="purple"))
plt.tight_layout(); plt.savefig(sys.argv[1] if len(sys.argv)>1 else "routed2.png",dpi=110); print("saved")

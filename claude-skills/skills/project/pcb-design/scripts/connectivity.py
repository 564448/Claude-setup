import re, sys
sys.argv=['x']
import numpy as np
from scipy.ndimage import label
import fixup as F, gen_kicad2 as G
s=open(__import__("os").path.join(__import__("os").environ.get("CANSAT_OUT",r"C:\Knight\Project\SPACE\Cansat\hardware"),"cansat.kicad_pcb"),encoding="utf-8").read()
names={v:k for k,v in G.NETID.items()}
tracks=[(names[int(m.group(7))],m.group(6),(float(m.group(1)),float(m.group(2))),(float(m.group(3)),float(m.group(4))),float(m.group(5))) for m in re.finditer(r'\(segment \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\) \(width ([-\d.]+)\) \(layer "([^"]+)"\) \(net (\d+)\)',s)]
vias=[(names[int(m.group(3))],float(m.group(1)),float(m.group(2))) for m in re.finditer(r'\(via \(at ([-\d.]+) ([-\d.]+)\) \(size [-\d.]+\) \(drill [-\d.]+\) \(layers "F.Cu" "B.Cu"\) \(net (\d+)\)',s)]
print(len(tracks),"segments",len(vias),"vias in PCB")
occ,padm=F.build_occ(tracks,vias); gi=F.gi; bad=[]
for net in G.NETS:
    if net=="GND": continue
    nid=G.NETID[net]; plist=[p for p in F.pads if p["net"]==net]
    if len(plist)<2: continue
    labs={L:label(occ[L]==nid)[0] for L in F.LAY}; parent={}
    def find(a):
        while parent.get(a,a)!=a: a=parent[a]
        return a
    def union(a,b):
        ra,rb=find(a),find(b)
        if ra!=rb: parent[ra]=rb
    for (n,x,y) in vias:
        if n==net and labs["F.Cu"][gi(y),gi(x)] and labs["B.Cu"][gi(y),gi(x)]: union(("F",labs["F.Cu"][gi(y),gi(x)]),("B",labs["B.Cu"][gi(y),gi(x)]))
    for pd in plist:
        if pd["th"]: union(("F",labs["F.Cu"][gi(pd["cy"]),gi(pd["cx"])]),("B",labs["B.Cu"][gi(pd["cy"]),gi(pd["cx"])]))
    comps={find((pd["layers"][0][0],labs[pd["layers"][0]][gi(pd["cy"]),gi(pd["cx"])])) for pd in plist}
    if len(comps)>1: bad.append((net,len(comps)))
print("nets not fully connected:",bad if bad else "none")
v=F.drc(tracks,vias); print("exact DRC on written PCB:",len(v))
for x in v[:10]: print("  ",x)

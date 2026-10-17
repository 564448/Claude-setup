import os, pcbnew, json
P=os.path.join(os.environ['CANSAT_OUT'],'cansat.kicad_pcb'); b=pcbnew.LoadBoard(P); MM=pcbnew.FromMM
segs=json.loads(os.environ["SEGS"]); n=0
for t in list(b.GetTracks()):
    if t.GetClass()!="PCB_TRACK": continue
    s,e=t.GetStart(),t.GetEnd()
    for (x0,y0,x1,y1) in segs:
        if (abs(s.x-MM(x0))<MM(0.03) and abs(s.y-MM(y0))<MM(0.03) and abs(e.x-MM(x1))<MM(0.03) and abs(e.y-MM(y1))<MM(0.03)) or (abs(e.x-MM(x0))<MM(0.03) and abs(e.y-MM(y0))<MM(0.03) and abs(s.x-MM(x1))<MM(0.03) and abs(s.y-MM(y1))<MM(0.03)):
            b.Delete(t); n+=1; break
print("deleted",n,"segments"); pcbnew.SaveBoard(P,b)

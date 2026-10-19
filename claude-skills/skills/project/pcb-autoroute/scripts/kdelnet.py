import os, pcbnew
P=os.path.join(os.environ['CANSAT_OUT'],'cansat.kicad_pcb'); b=pcbnew.LoadBoard(P); net=os.environ["NET"]; n=0
for t in list(b.GetTracks()):
    if t.GetNetname()==net: b.Delete(t); n+=1
print("deleted",n,"items of",net); pcbnew.SaveBoard(P,b)

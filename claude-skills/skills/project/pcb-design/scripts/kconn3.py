import os, pcbnew, sys
def say(*a): print(*a); sys.stdout.flush()
P=os.path.join(os.environ['CANSAT_OUT'],'cansat.kicad_pcb'); b=pcbnew.LoadBoard(P); mm=pcbnew.ToMM
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.BuildConnectivity(); c=b.GetConnectivity(); gnd=b.FindNet("GND").GetNetCode()
pads=[p for fp in b.GetFootprints() for p in fp.Pads() if p.GetNetCode()==gnd]
ref=[p for p in pads if p.GetParentFootprint().GetReference()=="U1" and p.GetNumber()=="1"][0]
def name(p): return f"{p.GetParentFootprint().GetReference()}-{p.GetNumber()}"
try:
    main={name(p) for p in c.GetConnectedPads(ref)}; say("A) GetConnectedPads: main cluster pads:",len(main))
    bad=[name(p)+f" @({mm(p.GetPosition().x):.2f},{mm(p.GetPosition().y):.2f})" for p in pads if name(p) not in main]
    say("   GND pads NOT in main cluster:",len(bad)); [say("    ",x) for x in bad]
except Exception as e: say("A) error",repr(e))
try:
    edges=c.GetRatsnestForNet(gnd); say("B) ratsnest edges:",len(edges))
    for e in edges: say("    ",mm(e.GetSourcePos().x),mm(e.GetSourcePos().y),"<->",mm(e.GetTargetPos().x),mm(e.GetTargetPos().y))
except Exception as e: say("B) error",repr(e))

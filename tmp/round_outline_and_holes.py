from pathlib import Path
from datetime import datetime
import json,shutil,math
import pcbnew as p

root=Path('hardware/schematic/v1.0/GPSDO_Rev1.0')
live=root/'GPSDO_Rev1.0.kicad_pcb'
b=p.LoadBoard(str(live))
assert not list(b.GetTracks()) and not list(b.Zones())
fps={f.GetReference():f for f in b.GetFootprints()}
X,Y=106.415,63.44
signature=lambda: sorted((f.m_Uuid.AsString(),f.GetReference(),f.GetValue(),q.m_Uuid.AsString(),q.GetNumber(),q.GetNetname()) for f in fps.values() for q in f.Pads())
before=signature()
edge=[x for x in b.GetDrawings() if x.GetLayer()==p.Edge_Cuts]
assert len(edge)==1 and edge[0].GetShape()==p.SHAPE_T_RECT
edge[0].SetCornerRadius(p.FromMM(3.7))
edge[0].SetWidth(p.FromMM(.05))

def move(ref,dx,dy):
 f=fps[ref];delta=p.VECTOR2I(p.FromMM(dx),p.FromMM(dy))
 f.Move(delta)

for ref,x,y in [('H1',5,5),('H2',70,5),('H3',5,70),('H4',70,70)]:
 f=fps[ref];f.SetPosition(p.VECTOR2I(p.FromMM(X+x),p.FromMM(Y+y)))
 f.Reference().SetPosition(f.GetPosition());f.Value().SetPosition(f.GetPosition())

# Retain both mutually exclusive OCXO options at their exact relative offset.
for ref in ['U5','U7']: move(ref,.5,.5)
move('R4',0,.5)

# Translate the complete GNSS electrical module away from the new top-right
# mounting-hole envelope. Internal RF/bypass placement is unchanged.
gnss=['U6','RF1','C6','C7','C8','FB8','L1','R1','R2','R3','R8','R9']
for ref in gnss: move(ref,-1.5,3)

parts=[f for f in fps.values() if not f.GetReference().startswith('H')]
body_overlap=[]
for i,a in enumerate(parts):
 for c in parts[i+1:]:
  if {a.GetReference(),c.GetReference()}=={'U5','U7'}: continue
  if a.GetBoundingBox(False,False).Intersects(c.GetBoundingBox(False,False)):
   body_overlap.append((a.GetReference(),c.GetReference()))
assert not body_overlap,body_overlap

# A circular mechanical envelope avoids treating the corner of the hole's
# rectangular bounding box as a real collision. 3.75 mm includes the pad
# radius and an additional placement allowance; screw hardware is unchanged.
hole_clearance=[]
for hole in ['H1','H2','H3','H4']:
 h=fps[hole].GetPosition();hx,hy=p.ToMM(h.x),p.ToMM(h.y)
 for f in parts:
  q=f.GetBoundingBox(False,False)
  xmin,ymin=p.ToMM(q.GetX()),p.ToMM(q.GetY())
  xmax,ymax=p.ToMM(q.GetRight()),p.ToMM(q.GetBottom())
  dx=max(xmin-hx,0,hx-xmax);dy=max(ymin-hy,0,hy-ymax)
  dist=math.hypot(dx,dy)
  if dist<3.75: hole_clearance.append((hole,f.GetReference(),round(dist,3)))
assert not hole_clearance,hole_clearance
assert signature()==before
backup=root/'.history'/('before_round_R3p7_holes5_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.kicad_pcb')
shutil.copy2(live,backup)
p.SaveBoard(str(live),b)
check=p.LoadBoard(str(live)); e=next(x for x in check.GetDrawings() if x.GetLayer()==p.Edge_Cuts)
assert abs(p.ToMM(e.GetCornerRadius())-3.7)<.00001
print('Board 75 x 75 mm, corner R3.7 mm, hole centres inset 5 mm.')
print('No unintended body collisions; all four 3.75 mm hole envelopes clear.')
print('Shifted GNSS module -1.5,+3 mm; OCXO options +0.5,+0.5 mm; R4 +0,+0.5 mm.')
print('Backup:',backup)
